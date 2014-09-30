module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        phase: {
            src: 'static',
        },

        jshint: {
            options: {
                jshintrc: 'jshintrc.json',
                reporter: require('jshint-stylish')
            },
            files: [
                'Gruntfile.js',
                '<%= phase.src %>/js/*.js',
                '<%= phase.src %>/js/**/*.js',
                '!<%= phase.src %>/js/vendor/*.js',
                '!bootstrap/**/*.js'
            ]
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');

    grunt.registerTask('default', ['jshint']);
};
