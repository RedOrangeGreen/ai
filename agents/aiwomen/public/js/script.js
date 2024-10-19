document.addEventListener('DOMContentLoaded', function() {
    const message = document.getElementById('message');
    if (message) {
        message.textContent = 'A selection of AI women. Who do you choose?';
    }

    const womenImageContainer = document.getElementById('womenimage');

    function updateImageAndMessage(profileName, imageSrc) {
        return async () => {
            const response = await fetch(`/profile/${profileName}`, { method: 'POST' });
            const text = await response.text();
            document.getElementById('womenmessage').textContent = text;

            // Clear previous image
            womenImageContainer.innerHTML = '';

            // Create and append new image
            const img = document.createElement('img');
            img.src = imageSrc;
            img.alt = `${profileName}'s image`;
            img.style.maxWidth = '100%'; // Ensure image is responsive
            womenImageContainer.appendChild(img);
        };
    }

    const colette = document.getElementById('colette');
    if (colette) {
        colette.addEventListener('click', updateImageAndMessage('colette', '/public/img/slide1.jpg'));
    }

    const gloria = document.getElementById('gloria');
    if (gloria) {
        gloria.addEventListener('click', updateImageAndMessage('gloria', '/public/img/slide2.jpg'));
    }

    const annika = document.getElementById('annika');
    if (annika) {
        annika.addEventListener('click', updateImageAndMessage('annika', '/public/img/slide3.jpg'));
    }
});
