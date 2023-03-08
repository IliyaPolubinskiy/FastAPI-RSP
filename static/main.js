const websocket = new WebSocket(`ws://${window.location.hostname}:8000/ws${window.location.pathname}`);
document.getElementById("roomnumber").innerHTML = window.location.pathname.slice(1)

function sendMessage(data) {
  websocket.send(data)
}

websocket.addEventListener('error', (event) => {console.log(event)})

function update_opponent_status(status) {
  let status_span = document.getElementById("status")
  if (status == true) {
    status_span.innerHTML = "ready"
  }
  if (status == false) {
    status_span.innerHTML = "not ready"
  }
}

function isReady() {
  let ready = document.getElementById("isReady")
  let label = document.getElementById("isReadyLabel")
  if (!ready.checked) {
    label.removeAttribute("class")
    label.setAttribute("class", "btn btn-outline-success my-1")
    label.innerHTML = "Ready"
    websocket.send(JSON.stringify({"command": "ready"}))
  } else {
    label.removeAttribute("class")
    label.setAttribute("class", "btn btn-outline-danger my-1")
    label.innerHTML = "Not ready"
    websocket.send(JSON.stringify({"command": "not ready"}))
  }
}

const startCountDown = setInterval(countDown, 1000)

function startGame() {
  const readyButton = document.getElementById("isReady")
  const tools = document.getElementsByClassName("tool")
  const timer = document.getElementById("timer")
  for (i in tools) {
    tools[i].disabled = false
  }
  timer.innerHTML = 3
  readyButton.disabled = true
  startCountDown
}

websocket.addEventListener("message", (event) => {
  let data = JSON.parse(event.data)
  if (data.connections) {
    document.getElementById("connections").innerHTML = data.connections
  }
  if (data.command) {
    let command = data.command;
    if (command == "start") {
      startGame()
    }
    if (command == "update_opponent_status") {
      update_opponent_status(data.opponent_status)
    }
  }
  if (data.result) {
    resultHandler(data.result)
  }
})



function makeNote(text, style, item_1, item_2) {
  let div = document.createElement('div')
  div.setAttribute("class", `alert alert-${style} d-flex align-items-center flex-column`)
  div.setAttribute("role", "alert")

  let svg = document.createElement('svg')
  svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
  svg.setAttribute("class", "bi bi-exclamation-triangle-fill flex-shrink-0 me-2")
  svg.setAttribute("role", "img")
  svg.setAttribute("aria-label", "Warning:")

  let path = document.createElement('path') 
  path.setAttribute("d", "M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z")

  let strong = document.createElement('strong')

  let p_with_result = document.createElement('p') 
  let item_1_p = document.createElement('p') 
  let item_2_p = document.createElement('p') 
  let result_text = document.createTextNode(text)
  let item_1_text = document.createTextNode(`Вы выбрали: ${item_1}`)
  let item_2_text = document.createTextNode(`Оппонент выбрал: ${item_2}`)
  p_with_result.appendChild(result_text)
  strong.appendChild(p_with_result)
  item_1_p.appendChild(item_1_text)
  item_2_p.appendChild(item_2_text)
  svg.appendChild(path)
  div.appendChild(svg)
  div.appendChild(strong)
  div.appendChild(item_1_p)
  div.appendChild(item_2_p)
  return div
}

function resultHandler(result) {
  let resultContainer = document.getElementById("resultContainer")
  if (result.win == true) {
    resultContainer.appendChild(makeNote("Вы выиграли!", "success", result.winner_item, result.loser_item))
  }
  if (result.win == false) {
    resultContainer.appendChild(makeNote("Вы проиграли!", "danger", result.loser_item, result.winner_item))
  }
  if (result.win == "no one") {
    resultContainer.appendChild(makeNote("Ничья!", "primary", result.item, result.item))
  }
  console.log(result)
}

function countDown() { 
  let timer = document.getElementById("timer")
  let num = parseInt(timer.innerHTML)
  if (num > 0) {
    timer.innerHTML = num - 1
  }
  if (num == 0) {
    clearInterval(startCountDown);
    onGameOver()
  }
}

function onGameOver() { 
  const tools = document.getElementsByClassName("tool")
  for (i in tools) {
    tools[i].disabled = true
    if (tools[i].checked == true) {
      pickedItem = tools[i].getAttribute("id")
    }
  }
  websocket.send(JSON.stringify({result: pickedItem}))
  console.log(JSON.stringify({result: pickedItem}))
  timer.innerHTML = ""
}

"setInterval(timer, 1000)"