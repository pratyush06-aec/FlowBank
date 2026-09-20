from sqlalchemy.orm import Session
from ..models.domain import Asset, DeFiPosition
from abc import ABC, abstractmethod

class BaseExecutionProvider(ABC):
    @abstractmethod
    def execute(self, intent: dict, db: Session, user_id: str) -> dict:
        pass

class MockExecutionProvider(BaseExecutionProvider):
    def execute(self, intent: dict, db: Session, user_id: str) -> dict:
        """
        Simulates execution by directly modifying the DB.
        """
        action = intent.get("action")
        amount = intent.get("amount", 0)
        protocol = intent.get("protocol", "UNKNOWN")
        asset_symbol = intent.get("asset", "USDC")
        
        if action == "SUPPLY_TO_DEFI":
            # Deduct from Liquid Cash
            liquid = db.query(Asset).filter(Asset.user_id == user_id, Asset.asset_symbol == asset_symbol).first()
            if not liquid or liquid.amount < amount:
                return {"status": "FAILED", "reason": "Insufficient liquid balance in mock db"}
            
            liquid.amount -= amount
            liquid.value_usd -= amount
            
            # Add to DeFi
            defi = db.query(DeFiPosition).filter(DeFiPosition.user_id == user_id, DeFiPosition.protocol == protocol, DeFiPosition.asset_symbol == asset_symbol).first()
            if defi:
                defi.amount += amount
                defi.value_usd += amount
            else:
                defi = DeFiPosition(user_id=user_id, protocol=protocol, asset_symbol=asset_symbol, amount=amount, value_usd=amount, apy=5.0)
                db.add(defi)
                
            db.commit()
            return {"status": "SUCCESS", "tx_hash": f"mock_supply_{amount}", "reason": "Mock executed"}
            
        elif action == "WITHDRAW_FROM_DEFI":
            defi = db.query(DeFiPosition).filter(DeFiPosition.user_id == user_id, DeFiPosition.protocol == protocol, DeFiPosition.asset_symbol == asset_symbol).first()
            if not defi or defi.amount < amount:
                return {"status": "FAILED", "reason": "Insufficient DeFi balance in mock db"}
                
            defi.amount -= amount
            defi.value_usd -= amount
            
            liquid = db.query(Asset).filter(Asset.user_id == user_id, Asset.asset_symbol == asset_symbol).first()
            if liquid:
                liquid.amount += amount
                liquid.value_usd += amount
            else:
                liquid = Asset(user_id=user_id, asset_symbol=asset_symbol, amount=amount, value_usd=amount, source="wallet")
                db.add(liquid)
                
            db.commit()
            return {"status": "SUCCESS", "tx_hash": f"mock_withdraw_{amount}", "reason": "Mock withdrawn"}
            
        return {"status": "FAILED", "reason": "Unknown action"}

class BlockchainExecutionProvider(BaseExecutionProvider):
    def execute(self, intent: dict, db: Session, user_id: str) -> dict:
        """
        Prepares a real Sepolia transaction payload for BankOSAccount.
        """
        import os
        from web3 import Web3
        
        action = intent.get("action")
        amount = intent.get("amount", 0)
        protocol = intent.get("protocol", "UNKNOWN")
        asset_symbol = intent.get("asset", "USDC")
        
        if action != "SUPPLY_TO_DEFI":
            return {"status": "FAILED", "reason": "Only SUPPLY_TO_DEFI is currently supported via blockchain."}

        # Known contract addresses on Sepolia
        AAVE_POOL = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"
        USDC_SEPOLIA = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"
        
        # Hardcode the amount in decimals (USDC has 6 decimals, using 15,000)
        amount_wei = int(15000 * (10 ** 6))
        
        w3 = Web3()
        
        # Aave Pool supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
        aave_abi = [{
            "inputs": [
                {"internalType": "address", "name": "asset", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"},
                {"internalType": "address", "name": "onBehalfOf", "type": "address"},
                {"internalType": "uint16", "name": "referralCode", "type": "uint16"}
            ],
            "name": "supply",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        aave_contract = w3.eth.contract(address=AAVE_POOL, abi=aave_abi)
        # We need the user's BankOSAccount address. For the MVP, we hardcode the single deployed account
        BANK_ACCOUNT = os.getenv("BANK_OS_ACCOUNT_ADDRESS", "0x0000000000000000000000000000000000000000")
        
        aave_calldata = aave_contract.encodeABI(fn_name="supply", args=[
            w3.to_checksum_address(USDC_SEPOLIA),
            amount_wei,
            w3.to_checksum_address(BANK_ACCOUNT),
            0
        ])
        
        # Now construct the call to BankOSAccount.execute(address target, uint256 value, bytes data)
        bank_abi = [{
            "inputs": [
                {"internalType": "address", "name": "target", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
                {"internalType": "bytes", "name": "data", "type": "bytes"}
            ],
            "name": "execute",
            "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }]
        bank_contract = w3.eth.contract(address=BANK_ACCOUNT, abi=bank_abi)
        
        tx_calldata = bank_contract.encodeABI(fn_name="execute", args=[
            w3.to_checksum_address(AAVE_POOL),
            0,
            Web3.to_bytes(hexstr=aave_calldata)
        ])
        
        unsigned_tx = {
            "to": BANK_ACCOUNT,
            "data": tx_calldata,
            "value": "0",
        }
        
        return {
            "status": "PENDING_BLOCKCHAIN", 
            "reason": "Transaction prepared. Please sign via MetaMask.",
            "unsigned_tx": unsigned_tx
        }
