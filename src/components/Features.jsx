function Features() {
    return (
        <section className="features" id="features">
            <h2>Why Choose PrePilot?</h2>

            <div className="feature-container">
                <div className="feature-card">
                    <h3>Readiness Prediction</h3>
                    <p>
                        A Random Forest model trained on 37 academic, coding
                        and preparation signals predicts whether your
                        readiness is Poor, Average, Good or Excellent.
                    </p>
                </div>

                <div className="feature-card">
                    <h3>Class Probabilities</h3>
                    <p>
                        Do not just see a label. See the probability of every
                        readiness class, so you know how close you are to the
                        next level.
                    </p>
                </div>

                <div className="feature-card">
                    <h3>Honest Model Card</h3>
                    <p>
                        92.89% accuracy and 90.38 Macro F1 on a 12,000-record
                        held-out test set, against a 47.11% baseline. The
                        numbers come from the model metadata, not marketing.
                    </p>
                </div>
            </div>
        </section>
    );
}

export default Features;
