function Features() {
    return (
        <section className="features" id="features">
            <h2>Why Choose PrePilot?</h2>

            <div className="feature-container">
                <div className="feature-card">
                    <h3>Readiness Prediction</h3>
                    <p>
                        A Random Forest model looks at 37 things - your
                        marks, coding and preparation - and tells you if you
                        are Poor, Average, Good or Excellent.
                    </p>
                </div>

                <div className="feature-card">
                    <h3>Chances for Each Class</h3>
                    <p>
                        Do not just see one word. See the chance for each
                        class, so you know how close you are to the next
                        level.
                    </p>
                </div>

                <div className="feature-card">
                    <h3>Honest Model Card</h3>
                    <p>
                        92.89% right and 90.38 Macro F1 on a test set of
                        12,000 records, against a 47.11% simple baseline.
                        These numbers come from the model's own test report,
                        not from ads.
                    </p>
                </div>
            </div>
        </section>
    );
}

export default Features;
