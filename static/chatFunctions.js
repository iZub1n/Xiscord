document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    var cname = document.querySelector('#dNameNB').innerHTML;

    // detect enter alongside click
    document.querySelector('#messageField').addEventListener("keydown", event => {
        if (event.key == "Enter") {
            document.getElementById("sendMsg").click();
        }
    });

    // on button click
    document.querySelector('#sendMsg').addEventListener("click", () => {
        let message = document.getElementById("messageField").value;
        let timestamp = new Date;
        timestamp = timestamp.toLocaleTimeString();

        socket.emit('send message', {'message': message}, timestamp);
        document.getElementById("messageField").value = '';
    });

    socket.on('connect', () => {

    socket.on('announce message', data => {
        let dataMod = [data.timestamp, data.user, data.message]
        add_message(dataMod);
})
})
});