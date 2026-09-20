'use client'

import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { useState, useEffect } from 'react'

export function ConnectWallet() {
  const [mounted, setMounted] = useState(false)
  const { address, isConnected } = useAccount()
  const { connectors, connect } = useConnect()
  const { disconnect } = useDisconnect()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <button className="bg-[#00E5FF] text-black brutal-shadow px-6 py-2 font-black uppercase border-4 border-black opacity-50 cursor-not-allowed">
        Loading...
      </button>
    )
  }

  if (isConnected) {
    return (
      <button 
        onClick={() => disconnect()}
        className="bg-black text-white px-6 py-2 font-bold border-4 border-black brutal-shadow hover:bg-gray-800 uppercase"
      >
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </button>
    )
  }

  return (
    <button 
      onClick={() => connect({ connector: connectors[0] })}
      className="bg-[#00E5FF] text-black brutal-shadow px-6 py-2 font-black uppercase border-4 border-black hover:bg-[#00b8cc] transition-colors"
    >
      Connect Wallet
    </button>
  )
}
