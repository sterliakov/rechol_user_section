/*
 * knockout-file-bindings
 * Copyright 2014 Muhammad Safraz Razik
 * All Rights Reserved.
 * Use, reproduction, distribution, and modification of this code is subject
 * to the terms and conditions of the MIT license, available at
 * http://www.opensource.org/licenses/mit-license.php
 *
 * Author: Muhammad Safraz Razik
 * Project: https://github.com/adrotec/knockout-file-bindings
 */

// ! This file was modified by me. Important modification places are marked
// - with comments starting with '// !'.
/* global ko */
(function (factory) {
  // Module systems magic dance.
  if (typeof require === 'function'
      && typeof exports === 'object'
      && typeof module === 'object') {
    // CommonJS or Node: hard-coded dependency on 'knockout'
    factory(require('knockout'));
  // eslint-disable-next-line no-undef
  } else if (typeof define === 'function' && define['amd']) {
    // AMD anonymous module with hard-coded dependency on 'knockout'
    // eslint-disable-next-line no-undef
    define(['knockout'], factory);
  } else {
    // <script> tag: use the global `ko` object, attaching a `mapping` property
    factory(ko);
  }
}(function (ko) {
  const ko_unwrap = ko.utils.unwrapObservable;

  const fileBindings = {
    customFileInputSystemOptions: {
      wrapperClass: 'custom-file-input-wrapper',
      fileNameClass: 'custom-file-input-file-name',
      buttonGroupClass: 'custom-file-input-button-group',
      buttonClass: 'custom-file-input-button',
      clearButtonClass: 'custom-file-input-clear-button',
      buttonTextClass: 'custom-file-input-button-text',
    },
    defaultOptions: {
      wrapperClass: 'input-group',
      fileNameClass: 'disabled form-control',
      noFileText: 'No file chosen',
      buttonGroupClass: 'input-group-btn',
      buttonClass: 'btn btn-primary',
      clearButtonClass: 'btn btn-default',
      buttonText: 'Choose File',
      changeButtonText: 'Change',
      clearButtonText: 'Clear',
      fileName: true,
      clearButton: true,
      onClear: function(fileData) {
        if (typeof fileData.clear === 'function')
          fileData.clear();
      },
    },
  };

  function extendOptions(defaultOptions, newOptions) {
    let options = {};
    for (const prop in defaultOptions) {
      options[prop] = (typeof newOptions[prop] !== 'undefined'
        ? newOptions[prop]
        : defaultOptions[prop]);
    }
    return options;
  }

  const windowURL = window.URL || window.webkitURL;

  ko.bindingHandlers.fileInput = {
    init: function(element, valueAccessor) {
      let fileData = ko_unwrap(valueAccessor()) || {};
      if (fileData.dataUrl)
        fileData.dataURL = fileData.dataUrl;
      if (fileData.objectUrl)
        fileData.objectURL = fileData.objectUrl;

      fileData.file = fileData.file || ko.observable();
      fileData.fileArray = fileData.fileArray || ko.observableArray([]);
      let currentAcceptValue = element.getAttribute('accept');
      fileData.fileTypes = (fileData.fileTypes
                            || ko.observable(currentAcceptValue));
      element.setAttribute('accept', fileData.fileTypes());

      fileData.clear = fileData.clear || function() {
        let kinds = ['objectURL', 'base64String',
          'binaryString', 'text', 'dataURL', 'arrayBuffer'];
        kinds.forEach(function(property) {
          if (fileData[property + 'Array']
              && ko.isObservable(fileData[property + 'Array'])) {
            let values = fileData[property + 'Array'];
            while (values().length && property === 'objectURL')
              windowURL.revokeObjectURL(values.splice(0, 1));
          }
          if (fileData[property]
              && ko.isObservable(fileData[property])) {
            fileData[property](null);
          }
        });
        element.value = '';
        fileData.file(null);
        fileData.fileArray([]);
      };

      function fillData(file, index, callback){
        if (fileData.objectURL && ko.isObservable(fileData.objectURL)) {
          const newUrl = file && windowURL.createObjectURL(file);
          if (newUrl) {
            let oldUrl = fileData.objectURL();
            if (oldUrl)
              windowURL.revokeObjectURL(oldUrl);
            fileData.objectURL(newUrl);
          }
        }

        if (fileData.base64String
            && ko.isObservable(fileData.base64String)
            && !(fileData.dataURL
               && ko.isObservable(fileData.dataURL)))
          fileData.dataURL = ko.observable(); // adding on demand
        if (fileData.base64StringArray
            && ko.isObservable(fileData.base64StringArray)
            && !(fileData.dataURLArray
               && ko.isObservable(fileData.dataURLArray)))
          fileData.dataURLArray = ko.observableArray();

        const fileProperties = ['binaryString', 'text',
          'dataURL', 'arrayBuffer'];
        let doneFileProperties = {};
        let doneFileArrayResult = {};
        const checkDoneFileProperties = function(doneProperty){
          let done = true;
          doneFileProperties[doneProperty] = true;
          fileProperties.forEach(function(property){
            done &&= doneFileProperties[property];
          });
          if (done)
            callback(doneFileArrayResult);
        };
        fileProperties.forEach(function(property){
          if (!(fileData[property]
              && ko.isObservable(fileData[property]))
              && !(fileData[property + 'Array']
                 && ko.isObservable(fileData[property + 'Array']))) {
            checkDoneFileProperties(property);
            return true;
          }
          if (!file) {
            checkDoneFileProperties(property);
            return true;
          }
          if (index === 0
              && fileData[property + 'Array']
              && ko.isObservable(fileData[property + 'Array'])){
            fileData[property + 'Array']([]);
            // when base64String is enabled, dataURL is added if not exists
            // (see code above)
            if (property === 'dataURL'
                && fileData.base64StringArray
                && ko.isObservable(fileData.base64StringArray))
              fileData.base64StringArray([]);
          }

          const reader = new FileReader();
          const method = ('readAs'
                          + (property.substr(0, 1).toUpperCase()
                          + property.substr(1)));
          reader.onload = function(e) {
            function fillDataToProperty(result, prop){
              if (index === 0
                  && fileData[prop]
                  && ko.isObservable(fileData[prop]))
                fileData[prop](result);
              if (fileData[prop + 'Array']
                  && ko.isObservable(fileData[prop + 'Array']))
                doneFileArrayResult[prop] = result;
            }
            if (method === 'readAsDataURL'
                && (fileData.base64String || fileData.base64StringArray)) {
              let resultParts = e.target.result.split(',');
              if (resultParts.length === 2)
                fillDataToProperty(resultParts[1], 'base64String');

            }
            fillDataToProperty(e.target.result, property);
            checkDoneFileProperties(property);
          };

          reader[method](file);
        });
      }

      fileData.fileArray.subscribe(function(fileArray){
        if (!fileArray.length){
          valueAccessor().valueHasMutated();
          return;
        }
        let doneFileArrayResultMap = {};
        let checkDoneFiles = function(doneIndex, doneFileArrayResult){
          let done = true;
          doneFileArrayResultMap[doneIndex] = doneFileArrayResult;
          for (let index in fileArray)
            done &&= doneFileArrayResultMap[index];
          if (done) {
            let resultGroupedArray = {};
            for (let key in doneFileArrayResultMap[0])
              if (!resultGroupedArray[key])
                resultGroupedArray[key] = [];
            for (let index in fileArray) {
              let doneFileArrayResult = doneFileArrayResultMap[index];
              for (let prop in resultGroupedArray)
                resultGroupedArray[prop].push(doneFileArrayResult[prop]);
            }
            for (let prop in resultGroupedArray){
              if (fileData[prop + 'Array']
                  && ko.isObservable(fileData[prop + 'Array']))
                fileData[prop + 'Array'](resultGroupedArray[prop]);
            }
            valueAccessor().valueHasMutated();
          }
        };
        fileArray.forEach(function(file, index){
          // setTimeout(function(){
          fillData(file, index, function(doneFileArrayResult){
            checkDoneFiles(index, doneFileArrayResult);
          });
          // }, index == 1 ? 1000 : 0); // timeout for testing issue #35
        });
      });

      element.onchange = function() {
        let file = this.files[0];
        let fileArray = [];
        if (file) {
          // FileList is not an array
          for (let i = 0; i < this.files.length; i++)
            fileArray.push(this.files[i]);
          fileData.file(file);
        }
        // set it once for subscriptions to work properly
        fileData.fileArray(fileArray);
      };

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        let fileData = ko_unwrap(valueAccessor()) || {};
        fileData.clear = undefined;
      });
    },
    update: function() {},
  };

  function matchFile(fileType, file) {
    if (fileType.startsWith('.'))
      return file.name.endsWith(fileType);
    else if (fileType.endsWith('/*'))
      return file.type.startsWith(fileType.slice(0, -1));
    else
      return file.type === fileType;
  }

  function validateDroppedFileType($fileInput, file) {
    if ($fileInput.length) {
      const accept = $fileInput.attr('accept');
      if (accept) {
        let fileMatched = false;
        const fileTypes = accept.split(',');

        $.each(fileTypes, function(){
          fileMatched ||= matchFile(this, file);
        });
        return fileMatched;
      }
    }
    return true;
  }

  ko.bindingHandlers.fileDrag = {
    update: function(element, valueAccessor) {
      let $element = $(element);
      let fileInput = $element.find('input[type=file]')[0];

      let fileData = ko_unwrap(valueAccessor()) || {};
      if (!$element.attr('file-drag-injected')) {
        $element.addClass('filedrag');
        const handler = function(e) {
          e.stopPropagation();
          e.preventDefault();
          if (e.type === 'dragover')
            $element.addClass('hover');
          else
            $element.removeClass('hover');

          if (e.type === 'drop' && e.dataTransfer) {
            let files = e.dataTransfer.files;
            let fileArray = [];
            let failedFiles = [];
            if (files.length) {
              $.each(files, function(i, file){
                if (validateDroppedFileType(fileInput, file))
                  fileArray.push(file);
                else
                  failedFiles.push(file);
              });
              fileData.file(fileArray.length ? fileArray[0] : {});
            }
            if (!fileArray.length)
              fileData.clear();
            if (failedFiles.length) {
              // handle bad file drop, fire off a file rejected event here
              let fileInputContext = ko.dataFor(fileInput);
              if (fileInputContext
                  && typeof fileInputContext.onInvalidFileDrop === 'function')
                fileInputContext.onInvalidFileDrop(failedFiles);
            }
            fileData.fileArray(fileArray);

            // ! ------ This part was added my me. ------
            // - Otherwise drag&drop does not show up in input.files
            // - so submission doesn't work
            let dt = new DataTransfer();
            $.each(fileArray, function(i, file){
              dt.items.add(file);
            });
            fileInput.files = dt.files;
            // ! ------------ End of mine ---------------
          }
        };
        element.ondragover = element.ondragleave = element.ondrop = handler;

        $element.attr('file-drag-injected', 1);
      }
    },
  };

  ko.bindingHandlers.customFileInput = {
    init: function(element, valueAccessor) {
      let options = ko_unwrap(valueAccessor());
      if (options === false)
        return;
      if (typeof options !== 'object')
        options = {};

      let sysOpts = fileBindings.customFileInputSystemOptions;
      let defOpts = fileBindings.defaultOptions;

      options = extendOptions(defOpts, options);

      let $element = $(element);
      let wrapper = $('<span>')
        .addClass(sysOpts.wrapperClass)
        .addClass(options.wrapperClass);
      let buttonGroup = $('<span>')
        .addClass(sysOpts.buttonGroupClass)
        .addClass(options.buttonGroupClass);
      let button = $('<span>').addClass(sysOpts.buttonClass);
      buttonGroup.append(button);
      wrapper.append(buttonGroup);
      $element.before(wrapper);
      button.append($element);

      if (options.fileName){
        let fileNameInput = $('<input type=text readonly />');
        buttonGroup.before(
          fileNameInput.addClass(sysOpts.fileNameClass));
        if (buttonGroup.hasClass('btn-group'))
          buttonGroup.removeClass('btn-group').addClass('input-group-btn');
      }
      else if (buttonGroup.hasClass('input-group-btn')) {
        buttonGroup.removeClass('input-group-btn').addClass('btn-group');
      }

      $element.before($('<span>').addClass(sysOpts.buttonTextClass));

    },
    update: function(element, valueAccessor, allBindingsAccessor) {
      let options = ko_unwrap(valueAccessor());
      if (options === false)
        return;
      if (typeof options !== 'object')
        options = {};

      const sysOpts = fileBindings.customFileInputSystemOptions;
      const defOpts = fileBindings.defaultOptions;

      options = extendOptions(defOpts, options);

      const allBindings = allBindingsAccessor();
      if (!allBindings.fileInput)
        return;

      let fileData = ko_unwrap(allBindings.fileInput) || {};
      let file = ko_unwrap(fileData.file);

      let $el = $(element);
      let button = $el.parent()
        .addClass(ko_unwrap(options.buttonClass));
      let buttonGroup = button.parent();
      let wrapper = buttonGroup.parent();

      let buttonText = button.find('.' + sysOpts.buttonTextClass);
      buttonText.text(ko_unwrap(file
        ? options.changeButtonText
        : options.buttonText));
      if (options.fileName){
        let fileNameInput = wrapper.find('.' + sysOpts.fileNameClass)
          .addClass(ko_unwrap(options.fileNameClass));

        if (file && file.name) {
          if (fileData.fileArray().length > 2)
            fileNameInput.val(fileData.fileArray().length + ' files');
          else
            fileNameInput.val(fileData.fileArray().map(f => f.name).join(', '));
        } else {
          fileNameInput.val(ko_unwrap(options.noFileText));
        }
      }

      let clearButton = buttonGroup.find('.' + sysOpts.clearButtonClass);
      if (!clearButton.length) {
        clearButton = $('<span>')
          .addClass(sysOpts.clearButtonClass)
          .click(() => options.onClear(fileData, options))
          .appendTo(buttonGroup);
      }
      clearButton.text(ko_unwrap(options.clearButtonText))
                 .addClass(ko_unwrap(options.clearButtonClass));

      if (!(file && options.clearButton && file.name))
        clearButton.remove();
    },
  };

  ko.fileBindings = fileBindings;
  return fileBindings;
}));

$(function(){
  $(document).on('click', '.custom-file-input-button', function(){
    $(this).find('input[type=file]').click();
  });
  $('input[type=file]').click(function(ev){
    ev.stopPropagation();
  });

  let viewModel = {
    fileData: ko.observable({
      dataURL: ko.observable(),
      file: ko.observable(),
      fileArray: ko.observableArray(),
    }),
    onClear: function(fileData){
      fileData && fileData.clear && fileData.clear();
    },
  };
  ko.applyBindings(viewModel);
});
