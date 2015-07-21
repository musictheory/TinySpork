var fs = require("fs");
var TinySpork = require("./TinySpork")


var spork = new TinySpork(9666, __dirname);


function build()
{
    spork.begin();

    var lines = fs.readFileSync("errors.log").toString().split("\n").forEach(function(line) {
        line = line.trim();
        if (line.length > 0) {
            spork.error(line);
        }
    });

    spork.end();
}


task("watch", function() {
    watcher = fs.watch(".", { persistent: true, recursive: true });

    watcher.on("change", function (event, filename) {
        build();
    });

    build();
});
