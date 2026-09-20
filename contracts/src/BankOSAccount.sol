// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BankOSAccount
 * @dev Simple smart account implementation for the BankOS MVP.
 * Provides a basic permission model where a "copilot" (backend) can execute 
 * transactions up to a certain limit or on specific protocols, while the 
 * owner has full control.
 */
contract BankOSAccount {
    address public owner;
    address public copilot;
    
    event Executed(address indexed target, uint256 value, bytes data);
    event CopilotUpdated(address indexed newCopilot);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier onlyAuthorized() {
        require(msg.sender == owner || msg.sender == copilot, "Not authorized");
        _;
    }

    constructor(address _owner, address _copilot) {
        owner = _owner;
        copilot = _copilot;
    }
    
    function setCopilot(address _copilot) external onlyOwner {
        copilot = _copilot;
        emit CopilotUpdated(_copilot);
    }
    
    /**
     * @dev Executes a transaction on behalf of the smart account.
     * In a production environment, this would include strict policy 
     * enforcement on-chain (e.g. only calling allowed Aave/Uniswap functions).
     * For this Hackathon MVP, the backend Risk and Policy engines enforce rules off-chain
     * before sending the transaction through the Copilot address.
     */
    function execute(address target, uint256 value, bytes calldata data) external onlyAuthorized returns (bytes memory) {
        (bool success, bytes memory result) = target.call{value: value}(data);
        require(success, "Transaction failed");
        
        emit Executed(target, value, data);
        return result;
    }
    
    receive() external payable {}
}
