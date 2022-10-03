// Select2 customization
$.fn.formattedDjangoSelect2 = function() {
  this.djangoSelect2({
    templateResult: function(state){
      if (state.placeholder)
        return state.placeholder;

      if ('undefined' !== typeof state.shortcut) {
        return $(`<p title="${state.description}">${state.shortcut}</p>`);
      } else if (state.text.includes('|@@|')){
        let parts = state.text.split('|@@|');
        if (!window.showPrivateDistinct)
          parts[1] = parts[1].replace(' (p)', '');
        return $(`<p title="${parts[1]}">${parts[0]}</p>`);
      } else {
        return $(`<p>${state.text}</p>`);
      }
    },
    templateSelection: function(state){
      if (state.placeholder)
        return state.placeholder;

      if ('undefined' !== typeof state.shortcut) {
        return $(`<p title="${state.description}">${state.shortcut}</p>`);
      } else if (state.text.includes('|@@|')){
        let parts = state.text.split('|@@|');
        if (!window.showPrivateDistinct)
          parts[1] = parts[1].replace(' (p)', '');
        state.text = parts[1];
        state.shortcut = parts[0];
        state.description = parts[1];
        return $(`<p title="${parts[1]}">${parts[0]}</p>`);
      } else {
        return $(`<p>${state.text}</p>`);
      }
    },
  });
  return this;
};

$.fn.select2.amd.require(['select2/selection/search'], function (Search) {
  var oldRemoveChoice = Search.prototype.searchRemoveChoice;

  Search.prototype.searchRemoveChoice = function () {
    oldRemoveChoice.apply(this, arguments);
    this.$search.val('');
  };
});

$(function(){
  const optionData = {
    id: -1,
    text: 'Search...',
  };
  const len_before = 5;
  function styleSearchOption(){
    let opts = $('#main-search .select2-results__options li');
    if (opts.length - 1 > len_before)
      opts.first().addClass('search-option');
    else
      opts.last().addClass('search-option');
  }

  $('#main-search select')
    .djangoSelect2({
      dropdownParent: $('#main-search'),
      ajax: {
        // cloned from dlango_select2.js
        data: function(params) {
          return {
            term: params.term,
            page: params.page,
            field_id: $('#main-search select').data('field_id'),
          };
        },
        processResults: function(data) {
          const results = (data.results.length > len_before
            ? [optionData, ...data.results]
            : [...data.results, optionData]);
          return {
            results: results,
            pagination: {
              more: data.more,
            },
          };
        },
        transport: function (params, success, failure) {
          return $.ajax(params)
            .then(function(data) {
              success(data);
              styleSearchOption();
            })
            .fail(failure);
        },
      },
    })
    .removeClass('select2-custom')
    .on('select2:select', function(ev) {
      const patId = ev.params.data.id;
      if (patId === optionData.id) {
        let uri = new URL(window.search_url, document.baseURI);
        uri.searchParams.set('q', window.search_term);
        window.location.href = uri;
      } else {
        window.location.href = window.patient_url(patId);
      }
    })
    .on('select2:selecting', function(){
      window.search_term = $('#main-search .select2-search__field').val();
    });
});
