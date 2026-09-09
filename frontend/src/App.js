import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import Home from "@/pages/Home";
import Gallery from "@/pages/Gallery";
import NftDetail from "@/pages/NftDetail";
import TraitLab from "@/pages/TraitLab";
import Perks from "@/pages/Perks";
import Admin from "@/pages/Admin";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

function Shell({ children }) {
  return (
    <div className="min-h-screen bg-[#08090D]">
      <Navbar />
      <main>{children}</main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Toaster position="top-right" theme="dark" richColors />
        <Routes>
          <Route path="/" element={<Shell><Home /></Shell>} />
          <Route path="/gremlins" element={<Shell><Gallery /></Shell>} />
          <Route path="/gremlin/:id" element={<Shell><NftDetail /></Shell>} />
          <Route path="/trait-lab" element={<Shell><TraitLab /></Shell>} />
          <Route path="/perks" element={<Shell><Perks /></Shell>} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
