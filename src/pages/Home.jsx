import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import Features from "../components/Features";
import PredictorForm from "../components/PredictorForm";
import Footer from "../components/Footer";

function Home() {
    return (
        <>
            <Navbar />
            <Hero />
            <Features />
            <PredictorForm />
            <Footer />
        </>
    );
}

export default Home;
