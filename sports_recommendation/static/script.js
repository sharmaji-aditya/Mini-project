document.getElementById('recommend-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const loader = document.getElementById('loader');
    loader.style.display = 'block';

    const requestData = {
        age: parseInt(document.getElementById('age').value),
        bmi: parseFloat(document.getElementById('bmi').value),
        goal: document.getElementById('goal').value.trim().toLowerCase(),
        preference: document.getElementById('preference').value.trim().toLowerCase()
    };

    fetch('http://localhost:5000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        loader.style.display = 'none';
        const recommendation = document.getElementById('result');
        recommendation.innerHTML = data.error ? data.error : `Recommended Sport: ${data.recommended_sport}`;
    })
    .catch(error => {
        loader.style.display = 'none';
        document.getElementById('result').innerHTML = 'An error occurred. Please try again later.';
    });
});
