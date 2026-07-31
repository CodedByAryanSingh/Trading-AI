import React, { useState } from 'react'

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true)
  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between mb-4">
          <button onClick={() => setIsLogin(true)} className={`px-3 py-2 ${isLogin ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>Login</button>
          <button onClick={() => setIsLogin(false)} className={`px-3 py-2 ${!isLogin ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>Register</button>
        </div>
        {isLogin ? (
          <form>
            <label className="block text-sm text-gray-600">Email</label>
            <input className="w-full border px-3 py-2 mb-3" />
            <label className="block text-sm text-gray-600">Password</label>
            <input type="password" className="w-full border px-3 py-2 mb-3" />
            <button className="w-full bg-indigo-600 text-white px-4 py-2 rounded">Sign in</button>
          </form>
        ) : (
          <form>
            <label className="block text-sm text-gray-600">Name</label>
            <input className="w-full border px-3 py-2 mb-3" />
            <label className="block text-sm text-gray-600">Email</label>
            <input className="w-full border px-3 py-2 mb-3" />
            <label className="block text-sm text-gray-600">Password</label>
            <input type="password" className="w-full border px-3 py-2 mb-3" />
            <button className="w-full bg-indigo-600 text-white px-4 py-2 rounded">Register</button>
          </form>
        )}
      </div>
    </div>
  )
}
