/* jshint node: true */

module.exports = function(grunt) {
  "use strict";

  // Project configuration.
  grunt.initConfig({

    // Metadata.
    pkg: grunt.file.readJSON('package.json'),
    banner: '/**\n' +
              '* <%= pkg.name %>.js v<%= pkg.version %> by @fat and @mdo\n' +
              '* Copyright <%= grunt.template.today("yyyy") %> <%= pkg.author %>\n' +
              '* <%= _.pluck(pkg.licenses, "url").join(", ") %>\n' +
              '*/\n',
    jqueryCheck: 'if (!jQuery) { throw new Error(\"Bootstrap requires jQuery\") }\n\n',
    bootstrap: 'bootstrap-src',
    dist: 'static',

    // Task configuration.
    clean: {
      dist: ['<%= dist %>']
    },

    concat: {
      options: {
        banner: '<%= banner %><%= jqueryCheck %>',
        stripBanners: false
      },
      bootstrap: {
        src: [
          '<%= bootstrap %>/js/transition.js',
          '<%= bootstrap %>/js/alert.js',
          '<%= bootstrap %>/js/button.js',
          '<%= bootstrap %>/js/carousel.js',
          '<%= bootstrap %>/js/collapse.js',
          '<%= bootstrap %>/js/dropdown.js',
          '<%= bootstrap %>/js/modal.js',
          '<%= bootstrap %>/js/tooltip.js',
          '<%= bootstrap %>/js/popover.js',
          '<%= bootstrap %>/js/scrollspy.js',
          '<%= bootstrap %>/js/tab.js',
          '<%= bootstrap %>/js/affix.js'
        ],
        dest: '<%= dist %>/js/<%= pkg.name %>.js'
      }
    },

    uglify: {
      options: {
        banner: '<%= banner %>'
      },
      bootstrap: {
        src: ['<%= concat.bootstrap.dest %>'],
        dest: '<%= dist %>/js/<%= pkg.name %>.min.js'
      }
    },

    recess: {
      options: {
        compile: true
      },
      bootstrap: {
        src: ['less/bootstrap.less'],
        dest: '<%= dist %>/css/<%= pkg.name %>.css'
      },
      min: {
        options: {
          compress: true
        },
        src: ['less/bootstrap.less'],
        dest: '<%= dist %>/css/<%= pkg.name %>.min.css'
      },
      theme: {
        src: ['less/theme.less'],
        dest: '<%= dist %>/css/<%= pkg.name %>-theme.css'
      },
      theme_min: {
        options: {
          compress: true
        },
        src: ['less/theme.less'],
        dest: '<%= dist %>/css/<%= pkg.name %>-theme.min.css'
      }
    },

    copy: {
      fonts: {
        expand: true,
        flatten: true,
        src: ["<%= bootstrap %>/fonts/*"],
        dest: '<%= dist %>/fonts/'
      }
    }

  });

  // These plugins provide necessary tasks.
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-recess');

  // JS distribution task.
  grunt.registerTask('dist-js', ['concat', 'uglify']);

  // CSS distribution task.
  grunt.registerTask('dist-css', ['recess']);

  // Fonts distribution task.
  grunt.registerTask('dist-fonts', ['copy']);

  // Full distribution task.
  grunt.registerTask('dist', ['clean', 'dist-css', 'dist-fonts', 'dist-js']);

  // Default task.
  grunt.registerTask('default', ['dist']);
};
