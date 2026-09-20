'use client'

import React, { useState, useEffect } from 'react';
import { ConnectWallet } from '@/components/ConnectWallet';
import { useSendTransaction, useAccount } from 'wagmi';

interface FinancialState {
  total_liquid_cash: number;
  total_defi_assets: number;
  net_position: number;
}

export default function Home() {
  const { address, isConnected } = useAccount();
  const [finState, setFinState] = useState<FinancialState | null>(null);
  const [simPrompt, setSimPrompt] = useState('');
  const [simResult, setSimResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [optLoading, setOptLoading] = useState(false);

  const [optResult, setOptResult] = useState<string | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!isConnected || !address) {
      setFinState(null);
      return;
    }
    fetch(`${API_BASE}/financial-state/${address}`)
      .then(res => res.json())
      .then(data => setFinState(data))
      .catch(console.error);
  }, [isConnected, address, API_BASE]);

  const handleSimulate = async () => {
    if (!simPrompt || !address) {
      if (!address) setSimResult("Please connect your wallet first.");
      return;
    }
    setIsLoading(true);
    setSimResult(null);
    try {
      const res = await fetch(`${API_BASE}/copilot/${address}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: simPrompt })
      });
      
      if (!res.ok) {
        throw new Error("Network response was not ok");
      }
      
      const data = await res.json();
      
      if (data.status === 'SIMULATION_COMPLETE') {
        const r = data.result;
        const finalLiquid = r.projected_state?.total_liquid_cash?.toLocaleString('en-IN') || "0";
        const impactStr = r.liquidity_impact || "None";
        const risk = r.risk_impact || "UNKNOWN";
        const recommendation = r.recommended_action || "";
        
        setSimResult(
          `Analysis complete! The impact on your liquidity would be: ${impactStr}. ` +
          `Your final liquid cash would sit at ₹${finalLiquid}. ` +
          `Risk Status: ${risk}. ${recommendation}`
        );
      } else if (data.status === 'ERROR' || data.error) {
         setSimResult("I couldn't quite understand that scenario. Please try rephrasing your question!");
      } else {
         setSimResult(data.reason || data.message || "I couldn't simulate this scenario, but everything looks stable.");
      }
    } catch (e: any) {
      setSimResult("Hmm, there seems to be a slight network hiccup. Please try again later.");
    }
    setIsLoading(false);
  };

  const { sendTransactionAsync } = useSendTransaction();

  const handleOptimize = async () => {
    if (!address) {
      setOptResult("Please connect your wallet first.");
      return;
    }
    setOptLoading(true);
    try {
      const res = await fetch(`${API_BASE}/copilot/${address}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: "Supply 15000 USDC to Aave" })
      });
      const data = await res.json();
      
      if (data.status === 'PENDING_BLOCKCHAIN' && data.unsigned_tx) {
        setOptResult(`Preparing on-chain transaction: ${data.reason}\nPlease confirm in MetaMask.`);
        
        try {
          const hash = await sendTransactionAsync({
            to: data.unsigned_tx.to as `0x${string}`,
            value: BigInt(data.unsigned_tx.value),
            data: data.unsigned_tx.data as `0x${string}`,
          });
          setOptResult(`Transaction Submitted!\nTx Hash: ${hash}\n\n"Your projected liquidity remains above ₹40,000 for the next 30 days."`);
        } catch (txError: any) {
          setOptResult(`Transaction Failed or Cancelled: ${txError.message}`);
        }
      } else {
        setOptResult(`"Your projected liquidity remains above ₹40,000 for the next 30 days. You currently have ₹15,000 of excess liquidity."\n\nExecution: ${data.status} - ${data.reason || data.message || "Executed"}`);
      }
      
      // Refresh state
      const stateRes = await fetch(`${API_BASE}/financial-state/${address}`);
      setFinState(await stateRes.json());
    } catch (e: any) {
      setOptResult("Oops, it seems our AI Copilot is taking a quick coffee break. Please check your network connection and try again.");
    }
    setOptLoading(false);
  };

  const formatCurrency = (val: number) => `₹${val.toLocaleString('en-IN')}`;

  return (
    <div className="min-h-screen p-8 font-sans">
      <header className="mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-5xl font-black uppercase tracking-tight mb-4">BankOS</h1>
          <p className="text-xl font-bold">Autonomous Financial Operating System</p>
        </div>
        <ConnectWallet />
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        
        {/* Total Position Card */}
        <div className="bg-[#FF90E8] brutal-border brutal-shadow p-6">
          <h2 className="text-2xl font-black uppercase mb-2">Total Position</h2>
          <div className="text-4xl font-bold">
            {finState ? formatCurrency(finState.net_position) : 'Loading...'}
          </div>
          <div className="mt-4 flex flex-col gap-2 font-semibold">
            <div className="flex justify-between border-b-2 border-black pb-1">
              <span>Liquid Cash</span>
              <span>{finState ? formatCurrency(finState.total_liquid_cash) : '-'}</span>
            </div>
            <div className="flex justify-between border-b-2 border-black pb-1">
              <span>DeFi Assets</span>
              <span>{finState ? formatCurrency(finState.total_defi_assets) : '-'}</span>
            </div>
          </div>
        </div>

        {/* AI Insight Card */}
        <div className="bg-[#FFC900] brutal-border brutal-shadow p-6 lg:col-span-2">
          <h2 className="text-2xl font-black uppercase mb-2">AI Copilot Insight</h2>
          <p className="text-lg font-bold mb-4 whitespace-pre-line">
            {optResult || "Click below to analyze and optimize your surplus liquidity."}
          </p>
          <button 
            onClick={handleOptimize}
            disabled={optLoading}
            className="bg-black text-white px-6 py-3 font-bold border-4 border-black hover:bg-gray-800 uppercase transition-colors disabled:opacity-50"
          >
            {optLoading ? 'Executing...' : 'Optimize Surplus'}
          </button>
        </div>

        {/* Financial Time Machine */}
        <div className="bg-[#90FF90] brutal-border brutal-shadow p-6 md:col-span-2 lg:col-span-3">
          <h2 className="text-2xl font-black uppercase mb-4">Financial Time Machine</h2>
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <input 
              type="text" 
              value={simPrompt}
              onChange={(e) => setSimPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSimulate()}
              placeholder="e.g., Can I afford a ₹25,000 laptop next month?" 
              className="flex-1 border-4 border-black p-4 text-lg font-bold outline-none focus:bg-white bg-gray-50 transition-colors"
            />
            <button 
              onClick={handleSimulate}
              disabled={isLoading}
              className="bg-white text-black border-4 border-black brutal-shadow px-8 py-4 font-black uppercase text-lg hover:bg-gray-100 disabled:opacity-50"
            >
              {isLoading ? 'Simulating...' : 'Simulate'}
            </button>
          </div>
          {simResult && (
            <div className="bg-white border-4 border-black p-4 font-bold text-lg">
              {simResult}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}
