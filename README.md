# Tiny Spork

Tiny Spork is a minuscule version of [Build Spork](https://github.com/musictheory/BuildSpork).  It eliminates the native UI application, and instead uses a TCP socket to send messages to sublime from a build script.

### Why?

[Sublime Text](http://www.sublimetext.com) includes support for build systems.  However, the support is very basic (projects have one designated build action, making it hard to support multiple targets with multiple build configurations).  Over time, the [musictheory.net](http://www.musictheory.net) build script outgrew this limited support.

More importantly, [Sublime Text](http://www.sublimetext.com) lacks real support for continuously running build systems.  Ideally, we want our build script running at all times, watching files, and starting builds.  When issues occur, a Sublime Text output panel appears.  When all issues are fixed, the output panel disappears.

### Usage

1. Copy TinySpork.py into your Sublime Text 3 `Packages` folder.
2. Open up this folder in Sublime Text 3
3. In Terminal, run `jake watch`

Open up `errors.log`, modify it, and save.  The contents will be sent to Sublime Text 3.
