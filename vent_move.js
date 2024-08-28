document.addEventListener('DOMContentLoaded', () => {
    // Ensure the vents data is correctly passed
    const vents = JSON.parse(document.getElementById('vents-data').textContent);
    console.log('Vents data:', vents);

    let currentIndex = 0;

    if (document.getElementById('leftArrow') && document.getElementById('rightArrow')) {
        document.getElementById('leftArrow').addEventListener('click', () => {
            console.log('Left arrow clicked');
            if (vents.length > 0) {
                currentIndex = (currentIndex - 1 + vents.length) % vents.length;
                document.getElementById('viewContent').innerText = vents[currentIndex].content;
                console.log('Current index after left arrow click:', currentIndex);
            }
        });

        document.getElementById('rightArrow').addEventListener('click', () => {
            console.log('Right arrow clicked');
            if (vents.length > 0) {
                currentIndex = (currentIndex + 1) % vents.length;
                document.getElementById('viewContent').innerText = vents[currentIndex].content;
                console.log('Current index after right arrow click:', currentIndex);
            }
        });
    }
});