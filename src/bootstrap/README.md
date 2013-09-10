This app makes customizing bootstrap using less possible in the scope of
this project.


## How to install

You need Grunt and npm to compile bootstrap.

  $ sudo npm install -g grunt-cli  # Will install globally
  $ npm install  # Will install required Node.js modules in `node_modules`

The bootstrap source is available as a Git submodule in `bootstrap-src`. Don't
forget to run those command if you just checked out the project:

  $ git submodule init
  $ git submodule update


## Building Bootstrap

To build Bootstrap, just run:

  $ grunt  # Easy, isn't it?


## Customizing Bootstrap

** Never modify anything in the bootstrap-src directory. ** You couldn't push it
on the bootstrap repository after commiting. Instead, update the files in the
local `less` directory, then build bootstrap again.

Static files should be build locally, then committed. Some people prefer building
in a task during the production release, but the first method is much cleaner and
less error prone.


## Upgrading Bootstrap

To upgrade the Bootstrap project, you need to use the git submodules features.

  $ cd bootstrap-src
  $ git pull  # Upgrade the git repository
  $ git tag  # list all tags
  $ git checkout vx.y.z  # Checkout the project to the newest version. Don't use master
  $ cd ..
  $ git add bootstrap-src
  $ git commit -m "Upgrade Bootstrap to vx.y.z"

Don't forget to re-generate static files.
