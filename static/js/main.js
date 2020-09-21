let trainingSetChoice1 = document.querySelector('#trainingSetChoice1');
let trainingSetChoice2 = document.querySelector('#trainingSetChoice2');

trainingSetChoice1.addEventListener('click', () => {
    let trainingSetDataDiv = document.querySelector('#trainingSetDataDiv');
    trainingSetDataDiv.classList.add("no-disp");
});

trainingSetChoice2.addEventListener('click', () => {
    let trainingSetDataDiv = document.querySelector('#trainingSetDataDiv');
    trainingSetDataDiv.classList.remove("no-disp");
});


let testingSetChoice1 = document.querySelector('#testingSetChoice1');
let testingSetChoice2 = document.querySelector('#testingSetChoice2');

testingSetChoice1.addEventListener('click', () => {
    let testingSetDataDiv = document.querySelector('#testingSetDataDiv');
    testingSetDataDiv.classList.add("no-disp");
});

testingSetChoice2.addEventListener('click', () => {
    let trainingSetDataDiv = document.querySelector('#testingSetDataDiv');
    testingSetDataDiv.classList.remove("no-disp");
});