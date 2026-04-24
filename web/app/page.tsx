import Hero from "@/components/Hero";
import Problem from "@/components/Problem";
import HowItWorks from "@/components/HowItWorks";
import Capabilities from "@/components/Capabilities";
import Demo from "@/components/Demo";
import Marketplace from "@/components/Marketplace";
import Creators from "@/components/Creators";
import About from "@/components/About";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";

export default function HomePage() {
  return (
    <main className="relative">
      <Nav />
      <Hero />
      <Problem />
      <HowItWorks />
      <Capabilities />
      <Demo />
      <Marketplace />
      <Creators />
      <About />
      <Footer />
    </main>
  );
}
