window.addEventListener('DOMContentLoaded', (event) => {

    // add background color to checked input

    let allInputs = document.getElementsByClassName('radio_btn');
    let formDiv = document.getElementsByClassName('controls')[0];
    checkIfSelectedChecked(allInputs, formDiv);

});


function checkIfSelectedChecked(inputList, formDiv) {

    for (let i = 0; i < inputList.length; i++) {
        inputList[i].addEventListener('change', (e) => {
            e.preventDefault()
            if (inputList[i].checked === true) {
                inputList[i].parentElement.style.background = "#007afd"
                inputList[i].parentElement.style.color = "white"
                let span = document.createElement('span')
                span.innerText = ' ✔ '
                span.style.color = 'white'
                inputList[i].parentElement.prepend(span)
            }
        })
    }

    formDiv.addEventListener('click', (e) => {
        for (let i = 0; i < inputList.length; i++) {
            inputList[i].parentElement.style.background = "white"
            inputList[i].parentElement.style.color = "#007afd"
            let spanToRemove = inputList[i].parentElement.getElementsByTagName('span')
            for (let i=0; i < spanToRemove.length; i++) {
                spanToRemove[i].remove()
            }
        }
    })
}

