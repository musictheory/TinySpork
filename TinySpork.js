var net = require("net");


function Connection(port)
{
    var lines = [ ];
    var connected = false;
    var closed = false;

    var socket = net.connect({ "port": port }, function() {
        connected = true;

        lines.forEach(function(line) {
            send(line);
        });

        if (closed) {
            socket.end();
        }
    });

    socket.on("error", function() {
        closed = true;
        connected = false;
    });

    function close() {
        closed = true;

        if (connected) {
            socket.end();
        }
    }

    function send(line){
        if (connected) {
            socket.write(line + "\n");
        } else {
            lines.push(line);
        }
    }

    return {
        send: send,
        close: close
    };
}


function TinySpork(port, projectDir)
{
    this._port       = port;
    this._projectDir = projectDir;
    this._connection = null;
}


TinySpork.prototype.begin = function()
{
    if (!this._connection) {
        this._connection = new Connection(this._port);
        this._connection.send("[begin] " + this._projectDir);
    }
}


TinySpork.prototype.notice = function(line)
{
    if (this._connection) {
        this._connection.send("[notice] " + line);
    }
}


TinySpork.prototype.error = function(line)
{
    if (this._connection) {
        this._connection.send(line);
    }
}


TinySpork.prototype.end = function()
{
    if (this._connection) {
        this._connection.send("[end]");
        this._connection.close();
        this._connection = null;
    }
}


module.exports = TinySpork;
