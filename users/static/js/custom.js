/* global PerfectScrollbar */

//eslint-disable-next-line no-unused-vars
function showAlert(text, type = 'warning'){
  const alert_btn = $(
    `<button type="button" data-dismiss="alert" aria-label="Close">
       <span aria-hidden="true">&times;</span>
     </button>`).addClass('close');
  const alert_body = $('<p>').addClass('mb-0');
  alert_body.text(text);
  const alert = $('<div role="alert">')
    .addClass(`alert alert-${type} alert-dismissible fade show`)
    .append(alert_body)
    .append(alert_btn);
  let parent = $('#main-wrapper');
  const best_parent = parent.find('sub_heading').next();
  parent = best_parent.length ? best_parent : parent;
  parent.children('.alert.alert-dismissible').slice(2).remove();
  parent.prepend(alert);
}

const Zenix = function() {
  'use strict';
  const e = $(window).width();
  const t = function() {
    $('#preloader').fadeOut(500);
    $('#main-wrapper').addClass('show');
  };
  const n = function() {
    const e = $(window).height() - 206;
    $('.chatbox .msg_card_body').css('height', e);
  };
  return {
    init: function(){
      t();
      $('.dz-scroll').each(function() {
        new PerfectScrollbar('#' + this.id, {
          wheelSpeed: 2,
          wheelPropagation: !0,
          minScrollbarLength: 20,
        }).isRtl = !1;
      });
      if (e <= 991){
        $('.menu-tabs .nav-link').on('click', function() {
          if ($(this).hasClass('open')) {
            $(this).removeClass('open');
            $('.fixed-content-box').removeClass('active');
          } else {
            $('.menu-tabs .nav-link').removeClass('open');
            $(this).addClass('open');
            $('.fixed-content-box').addClass('active');
          }
        });
      }
      $('.bell-link').on('click', function() {
        $('.chatbox').addClass('active');
      });
      $('.chatbox-close').on('click', function() {
        $('.chatbox').removeClass('active');
      });
      $('.dz-chat-user-box .dz-chat-user').on('click', function() {
        $('.dz-chat-user-box').addClass('d-none');
        $('.dz-chat-history-box').removeClass('d-none');
      });
      $('.dz-chat-history-back').on('click', function() {
        $('.dz-chat-user-box').removeClass('d-none');
        $('.dz-chat-history-box').addClass('d-none');
      });
      $('.custom-file-input').on('change', function() {
        var e = $(this).val().split('\\').pop();
        $(this).siblings('.custom-file-label').addClass('selected').html(e);
      });
      n();
    },
    load: function(){
      t();
      if ($('.default-select').length > 0)
        $('.default-select').selectpicker();
    },
    resize: function(){
      n();
    },
  };
}();

$(document).ready(function(){
  Zenix.init();
  $('body').append($('.modal'));

  // Preserve search url part with pagination and other anchors
  $('a[rel="keep-params"]').each(function(){
    const $this = $(this);
    const oldHref = $this.attr('href');
    const uri = new URL(oldHref, window.location.href);
    new URL(window.location.href).searchParams
      .forEach((v, k) => !uri.searchParams.has(k) && uri.searchParams.set(k, v));
    $this.attr('href', uri.toString());
  });
});
$(window).on('load', function(){
  Zenix.load();
});
$(window).on('resize', function(){
  Zenix.resize();
});

$.fn.serializeObject = function(){
  let o = {}, a = this.serializeArray();
  $.each(a, function() {
    if (o[this.name]) {
      if (!o[this.name].push)
        o[this.name] = [o[this.name]];
      o[this.name].push(this.value || '');
    } else {
      o[this.name] = this.value || '';
    }
  });
  return o;
};

if (!String.prototype.format) {
  String.prototype.format = function(kwargs) {
    return this.replace(
      /{(\w+)}/g,
      (match, key) => typeof kwargs[key] != 'undefined' ? kwargs[key] : match,
    );
  };
}

$.fn.initPhonePicker = function(number){
  const codeSel = $(this).addClass('phone-widget-wrapper')
    .find('select')
    .attr('data-container', 'body')
    .attr('data-live-search', 'true');
  codeSel.find('option').each(function(){
    const $this = $(this);
    $this.attr('title', $this.attr('value'));
  });
  if (typeof number !== 'undefined'){
    codeSel.find('option').prop('selected', false)
      .filter(`[value="${number[0]}"]`).prop('selected', true);
    codeSel.find('+ input').val(number[1]);
  }
  codeSel.selectpicker();
};

window.DATE_FORMAT = 'DD/MM/YYYY';

// Show modal and wait for response
// eslint-disable-next-line no-unused-vars
function inputDialog(dialog, selector){
  dialog.modal('show');
  return new Promise(function(resolve, reject){
    dialog
      .find('button[data-custom-action=confirm]')
      .on('click.promptDialog', function(ev){
        const selection = selector(dialog, ev);
        // Nothing selected
        if ('undefined' === typeof selection)
          return;

        dialog.off('hidden.bs.modal.promptDialog').modal('hide');
        dialog.on('hidden.bs.modal.promptDialog', function(){
          dialog
            .off('hidden.bs.modal.promptDialog')
            .find('button[data-custom-action]')
            .off('click.promptDialog');
          resolve(selection);
        });
      });
    dialog.on('hidden.bs.modal.promptDialog', function(){
      dialog
        .off('hidden.bs.modal.promptDialog')
        .find('button[data-custom-action]')
        .off('click.promptDialog');
      if (!dialog.hasClass('show'))
        return;
      reject('Cancelled');
    });
  }).catch(() => new Error('No user answer'));
}

$(function(){
  if (typeof moment !== 'undefined')
    moment.locale('ru');

  const h = window.innerHeight - $('#header').height();
  $('.content-body').css({
    'max-height': h,
    'height': h,
  });
});
