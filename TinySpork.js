
"use strict";

const net = require("net");
const fs  = require("fs");


class Connection {

    constructor()
    {
        this._lines     = [ ];
        this._closed    = false;

        let socket = net.createConnection("/tmp/TinySpork.sock", () => {
            this._socket = socket;

            this._lines.forEach(line => {
                this.send(line);
            });

            if (this._closed) {
                this._socket.end();
            }
        });

        socket.on("error", () => {
            this._closed = true;
            this._socket = null;
        })
    }

    close()
    {
        this._closed = true;

        if (this._socket) {
            this._socket.end();
            this._socket = null;
        }
    }


    send(line)
    {
        if (this._socket) {
            this._socket.write(line + "\n");
        } else {
            this._lines.push(line);
        }    
    }
}


module.exports = class TinySpork {

    constructor(projectDir)
    {
        this._projectDir = projectDir;
        this._connection = null;
    }

    begin()
    {
        if (!this._connection) {
            this._connection = new Connection();
            this._connection.send("[begin] " + this._projectDir);
        }
    }

    info(line)
    {
        if (this._connection) {
            this._connection.send("[info] " + line);
        }
    }

    error(lineOrLines)
    {
        if (this._connection) {
            if (Array.isArray(lineOrLines)) {
                if (lineOrLines.length) {
                    this._connection.send("[start-lines]");
                    lineOrLines.forEach(line => { this._connection.send(line); })
                    this._connection.send("[end-lines]");
                }

            } else {
                this._connection.send(line);
            }
        }
    }

    end()
    {
        if (this._connection) {
            this._connection.send("[end]");
            this._connection.close();
            this._connection = null;
        }
    }

}
