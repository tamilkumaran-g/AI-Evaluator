// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBcAbvrXrzSIynflQdBYJYmtZ9OpN3hBg8",
  authDomain: "myve-ai.firebaseapp.com",
  projectId: "myve-ai",
  storageBucket: "myve-ai.firebasestorage.app",
  messagingSenderId: "829097964158",
  appId: "1:829097964158:web:1204a44c661623cb871e2f",
  measurementId: "G-QVVGGYEQ7W"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export { app };
