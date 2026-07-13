"use client";
import{createContext,useContext,useMemo,useState}from"react";import{connectWallet}from"@/lib/genlayer";
type C={address:string;busy:boolean;error:string;connect:()=>Promise<void>};const Context=createContext<C|null>(null);
export function WalletProvider({children}:{children:React.ReactNode}){const[address,setAddress]=useState("");const[busy,setBusy]=useState(false);const[error,setError]=useState("");async function connect(){setBusy(true);setError("");const r=await connectWallet();if(r.success)setAddress(String(r.data||""));else setError(r.error||"Wallet connection failed");setBusy(false)}const value=useMemo(()=>({address,busy,error,connect}),[address,busy,error]);return <Context.Provider value={value}>{children}</Context.Provider>}
export function useWallet(){const v=useContext(Context);if(!v)throw new Error("WalletProvider missing");return v}
