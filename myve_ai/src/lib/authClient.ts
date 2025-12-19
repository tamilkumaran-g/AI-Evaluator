// src/lib/authClient.ts
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "../firebase";

export async function loginWithGoogle(): Promise<{
  idToken: string;
  uid: string;
  email: string | null;
  displayName: string | null;
}> {
  const result = await signInWithPopup(auth, googleProvider);
  const user = result.user;
  const idToken = await user.getIdToken();

  return {
    idToken,
    uid: user.uid,
    email: user.email,
    displayName: user.displayName,
  };
}