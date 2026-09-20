import os
import json
from groq import Groq
from sqlalchemy.orm import Session
from .policy_engine import PolicyEngine
from .risk_engine import RiskEngine
from ..services.execution_provider import BlockchainExecutionProvider

class AICopilot:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        api_key = os.getenv("GROQ_API_KEY")
        # Initialize Groq client
        self.client = Groq(api_key=api_key)
        self.policy_engine = PolicyEngine(db, user_id)
        self.risk_engine = RiskEngine(db, user_id)
        self.executor = BlockchainExecutionProvider() # Using Blockchain for Sepolia testnet

    def parse_intent(self, prompt: str) -> dict:
        """
        Uses Groq and Llama 3 to parse the user's natural language into a structured JSON intent.
        """
        system_prompt = """
        You are BankOS AI, an intent parser for an autonomous financial system.
        Extract the intent from the user's prompt and return ONLY a valid JSON object.
        Supported actions: "SUPPLY_TO_DEFI", "WITHDRAW_FROM_DEFI", "SIMULATE", "QUERY".
        If the user asks "what happens if" or "can I afford", return action: "SIMULATE" and populate "scenario_params" with "type", "amount".
        Format: {"action": "ACTION", "protocol": "PROTOCOL", "asset": "ASSET", "amount": 0, "scenario_params": {}}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            return {"action": "ERROR", "reason": str(e)}

    def process_prompt(self, prompt: str) -> dict:
        # 1. Parse Intent
        intent = self.parse_intent(prompt)
        action = intent.get("action")
        
        if action in ["SUPPLY_TO_DEFI", "WITHDRAW_FROM_DEFI"]:
            # 2. Check Policy
            policy_res = self.policy_engine.check_transaction(intent)
            if not policy_res["allowed"]:
                return {"status": "DENIED_BY_POLICY", "reason": policy_res["reason"], "intent": intent}
                
            # 3. Check Risk
            risk_res = self.risk_engine.evaluate_intent(intent)
            if not risk_res["safe"]:
                return {"status": "DENIED_BY_RISK", "reason": risk_res["reason"], "intent": intent}
                
            if policy_res["requires_approval"]:
                return {"status": "APPROVAL_REQUIRED", "reason": policy_res["reason"], "intent": intent}
                
            # 4. Execute (Mock for now)
            exec_res = self.executor.execute(intent, self.db, self.user_id)
            return {"status": exec_res["status"], "reason": exec_res["reason"], "tx_hash": exec_res.get("tx_hash"), "intent": intent}
            
        elif action == "SIMULATE":
            from ..services.simulator import simulate_scenario
            scenario_params = intent.get("scenario_params", {})
            sim_res = simulate_scenario(self.user_id, self.db, scenario_params)
            return {"status": "SIMULATION_COMPLETE", "result": sim_res, "intent": intent}
            
        return {"status": "SUCCESS", "message": "Query processed", "intent": intent}
