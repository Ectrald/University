
//translator.js only for internal usage

// 1) https://unpkg.com/popper.js@1
// for internal use
/*
 Copyright (C) Federico Zivolo 2019
 Distributed under the MIT License (license terms are at http://opensoˀurce.org/licenses/MIT).
 */(function (e, t) { 'object' == typeof exports && 'undefined' != typeof module ? module.exports = t() : 'function' == typeof define && define.amd ? define(t) : e.Popper = t() })(this, function () { 'use strict'; function e(e) { return e && '[object Function]' === {}.toString.call(e) } function t(e, t) { if (1 !== e.nodeType) return []; var o = e.ownerDocument.defaultView, n = o.getComputedStyle(e, null); return t ? n[t] : n } function o(e) { return 'HTML' === e.nodeName ? e : e.parentNode || e.host } function n(e) { if (!e) return document.body; switch (e.nodeName) { case 'HTML': case 'BODY': return e.ownerDocument.body; case '#document': return e.body; }var i = t(e), r = i.overflow, p = i.overflowX, s = i.overflowY; return /(auto|scroll|overlay)/.test(r + s + p) ? e : n(o(e)) } function r(e) { return 11 === e ? pe : 10 === e ? se : pe || se } function p(e) { if (!e) return document.documentElement; for (var o = r(10) ? document.body : null, n = e.offsetParent || null; n === o && e.nextElementSibling;)n = (e = e.nextElementSibling).offsetParent; var i = n && n.nodeName; return i && 'BODY' !== i && 'HTML' !== i ? -1 !== ['TH', 'TD', 'TABLE'].indexOf(n.nodeName) && 'static' === t(n, 'position') ? p(n) : n : e ? e.ownerDocument.documentElement : document.documentElement } function s(e) { var t = e.nodeName; return 'BODY' !== t && ('HTML' === t || p(e.firstElementChild) === e) } function d(e) { return null === e.parentNode ? e : d(e.parentNode) } function a(e, t) { if (!e || !e.nodeType || !t || !t.nodeType) return document.documentElement; var o = e.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING, n = o ? e : t, i = o ? t : e, r = document.createRange(); r.setStart(n, 0), r.setEnd(i, 0); var l = r.commonAncestorContainer; if (e !== l && t !== l || n.contains(i)) return s(l) ? l : p(l); var f = d(e); return f.host ? a(f.host, t) : a(e, d(t).host) } function l(e) { var t = 1 < arguments.length && void 0 !== arguments[1] ? arguments[1] : 'top', o = 'top' === t ? 'scrollTop' : 'scrollLeft', n = e.nodeName; if ('BODY' === n || 'HTML' === n) { var i = e.ownerDocument.documentElement, r = e.ownerDocument.scrollingElement || i; return r[o] } return e[o] } function f(e, t) { var o = 2 < arguments.length && void 0 !== arguments[2] && arguments[2], n = l(t, 'top'), i = l(t, 'left'), r = o ? -1 : 1; return e.top += n * r, e.bottom += n * r, e.left += i * r, e.right += i * r, e } function m(e, t) { var o = 'x' === t ? 'Left' : 'Top', n = 'Left' == o ? 'Right' : 'Bottom'; return parseFloat(e['border' + o + 'Width'], 10) + parseFloat(e['border' + n + 'Width'], 10) } function h(e, t, o, n) { return ee(t['offset' + e], t['scroll' + e], o['client' + e], o['offset' + e], o['scroll' + e], r(10) ? parseInt(o['offset' + e]) + parseInt(n['margin' + ('Height' === e ? 'Top' : 'Left')]) + parseInt(n['margin' + ('Height' === e ? 'Bottom' : 'Right')]) : 0) } function c(e) { var t = e.body, o = e.documentElement, n = r(10) && getComputedStyle(o); return { height: h('Height', t, o, n), width: h('Width', t, o, n) } } function g(e) { return fe({}, e, { right: e.left + e.width, bottom: e.top + e.height }) } function u(e) { var o = {}; try { if (r(10)) { o = e.getBoundingClientRect(); var n = l(e, 'top'), i = l(e, 'left'); o.top += n, o.left += i, o.bottom += n, o.right += i } else o = e.getBoundingClientRect() } catch (t) { } var p = { left: o.left, top: o.top, width: o.right - o.left, height: o.bottom - o.top }, s = 'HTML' === e.nodeName ? c(e.ownerDocument) : {}, d = s.width || e.clientWidth || p.right - p.left, a = s.height || e.clientHeight || p.bottom - p.top, f = e.offsetWidth - d, h = e.offsetHeight - a; if (f || h) { var u = t(e); f -= m(u, 'x'), h -= m(u, 'y'), p.width -= f, p.height -= h } return g(p) } function b(e, o) { var i = 2 < arguments.length && void 0 !== arguments[2] && arguments[2], p = r(10), s = 'HTML' === o.nodeName, d = u(e), a = u(o), l = n(e), m = t(o), h = parseFloat(m.borderTopWidth, 10), c = parseFloat(m.borderLeftWidth, 10); i && s && (a.top = ee(a.top, 0), a.left = ee(a.left, 0)); var b = g({ top: d.top - a.top - h, left: d.left - a.left - c, width: d.width, height: d.height }); if (b.marginTop = 0, b.marginLeft = 0, !p && s) { var w = parseFloat(m.marginTop, 10), y = parseFloat(m.marginLeft, 10); b.top -= h - w, b.bottom -= h - w, b.left -= c - y, b.right -= c - y, b.marginTop = w, b.marginLeft = y } return (p && !i ? o.contains(l) : o === l && 'BODY' !== l.nodeName) && (b = f(b, o)), b } function w(e) { var t = 1 < arguments.length && void 0 !== arguments[1] && arguments[1], o = e.ownerDocument.documentElement, n = b(e, o), i = ee(o.clientWidth, window.innerWidth || 0), r = ee(o.clientHeight, window.innerHeight || 0), p = t ? 0 : l(o), s = t ? 0 : l(o, 'left'), d = { top: p - n.top + n.marginTop, left: s - n.left + n.marginLeft, width: i, height: r }; return g(d) } function y(e) { var n = e.nodeName; if ('BODY' === n || 'HTML' === n) return !1; if ('fixed' === t(e, 'position')) return !0; var i = o(e); return !!i && y(i) } function E(e) { if (!e || !e.parentElement || r()) return document.documentElement; for (var o = e.parentElement; o && 'none' === t(o, 'transform');)o = o.parentElement; return o || document.documentElement } function v(e, t, i, r) { var p = 4 < arguments.length && void 0 !== arguments[4] && arguments[4], s = { top: 0, left: 0 }, d = p ? E(e) : a(e, t); if ('viewport' === r) s = w(d, p); else { var l; 'scrollParent' === r ? (l = n(o(t)), 'BODY' === l.nodeName && (l = e.ownerDocument.documentElement)) : 'window' === r ? l = e.ownerDocument.documentElement : l = r; var f = b(l, d, p); if ('HTML' === l.nodeName && !y(d)) { var m = c(e.ownerDocument), h = m.height, g = m.width; s.top += f.top - f.marginTop, s.bottom = h + f.top, s.left += f.left - f.marginLeft, s.right = g + f.left } else s = f } i = i || 0; var u = 'number' == typeof i; return s.left += u ? i : i.left || 0, s.top += u ? i : i.top || 0, s.right -= u ? i : i.right || 0, s.bottom -= u ? i : i.bottom || 0, s } function x(e) { var t = e.width, o = e.height; return t * o } function O(e, t, o, n, i) { var r = 5 < arguments.length && void 0 !== arguments[5] ? arguments[5] : 0; if (-1 === e.indexOf('auto')) return e; var p = v(o, n, r, i), s = { top: { width: p.width, height: t.top - p.top }, right: { width: p.right - t.right, height: p.height }, bottom: { width: p.width, height: p.bottom - t.bottom }, left: { width: t.left - p.left, height: p.height } }, d = Object.keys(s).map(function (e) { return fe({ key: e }, s[e], { area: x(s[e]) }) }).sort(function (e, t) { return t.area - e.area }), a = d.filter(function (e) { var t = e.width, n = e.height; return t >= o.clientWidth && n >= o.clientHeight }), l = 0 < a.length ? a[0].key : d[0].key, f = e.split('-')[1]; return l + (f ? '-' + f : '') } function L(e, t, o) { var n = 3 < arguments.length && void 0 !== arguments[3] ? arguments[3] : null, i = n ? E(t) : a(t, o); return b(o, i, n) } function S(e) { var t = e.ownerDocument.defaultView, o = t.getComputedStyle(e), n = parseFloat(o.marginTop || 0) + parseFloat(o.marginBottom || 0), i = parseFloat(o.marginLeft || 0) + parseFloat(o.marginRight || 0), r = { width: e.offsetWidth + i, height: e.offsetHeight + n }; return r } function T(e) { var t = { left: 'right', right: 'left', bottom: 'top', top: 'bottom' }; return e.replace(/left|right|bottom|top/g, function (e) { return t[e] }) } function C(e, t, o) { o = o.split('-')[0]; var n = S(e), i = { width: n.width, height: n.height }, r = -1 !== ['right', 'left'].indexOf(o), p = r ? 'top' : 'left', s = r ? 'left' : 'top', d = r ? 'height' : 'width', a = r ? 'width' : 'height'; return i[p] = t[p] + t[d] / 2 - n[d] / 2, i[s] = o === s ? t[s] - n[a] : t[T(s)], i } function D(e, t) { return Array.prototype.find ? e.find(t) : e.filter(t)[0] } function N(e, t, o) { if (Array.prototype.findIndex) return e.findIndex(function (e) { return e[t] === o }); var n = D(e, function (e) { return e[t] === o }); return e.indexOf(n) } function P(t, o, n) { var i = void 0 === n ? t : t.slice(0, N(t, 'name', n)); return i.forEach(function (t) { t['function'] && console.warn('`modifier.function` is deprecated, use `modifier.fn`!'); var n = t['function'] || t.fn; t.enabled && e(n) && (o.offsets.popper = g(o.offsets.popper), o.offsets.reference = g(o.offsets.reference), o = n(o, t)) }), o } function k() { if (!this.state.isDestroyed) { var e = { instance: this, styles: {}, arrowStyles: {}, attributes: {}, flipped: !1, offsets: {} }; e.offsets.reference = L(this.state, this.popper, this.reference, this.options.positionFixed), e.placement = O(this.options.placement, e.offsets.reference, this.popper, this.reference, this.options.modifiers.flip.boundariesElement, this.options.modifiers.flip.padding), e.originalPlacement = e.placement, e.positionFixed = this.options.positionFixed, e.offsets.popper = C(this.popper, e.offsets.reference, e.placement), e.offsets.popper.position = this.options.positionFixed ? 'fixed' : 'absolute', e = P(this.modifiers, e), this.state.isCreated ? this.options.onUpdate(e) : (this.state.isCreated = !0, this.options.onCreate(e)) } } function W(e, t) { return e.some(function (e) { var o = e.name, n = e.enabled; return n && o === t }) } function B(e) { for (var t = [!1, 'ms', 'Webkit', 'Moz', 'O'], o = e.charAt(0).toUpperCase() + e.slice(1), n = 0; n < t.length; n++) { var i = t[n], r = i ? '' + i + o : e; if ('undefined' != typeof document.body.style[r]) return r } return null } function H() { return this.state.isDestroyed = !0, W(this.modifiers, 'applyStyle') && (this.popper.removeAttribute('x-placement'), this.popper.style.position = '', this.popper.style.top = '', this.popper.style.left = '', this.popper.style.right = '', this.popper.style.bottom = '', this.popper.style.willChange = '', this.popper.style[B('transform')] = ''), this.disableEventListeners(), this.options.removeOnDestroy && this.popper.parentNode.removeChild(this.popper), this } function A(e) { var t = e.ownerDocument; return t ? t.defaultView : window } function M(e, t, o, i) { var r = 'BODY' === e.nodeName, p = r ? e.ownerDocument.defaultView : e; p.addEventListener(t, o, { passive: !0 }), r || M(n(p.parentNode), t, o, i), i.push(p) } function F(e, t, o, i) { o.updateBound = i, A(e).addEventListener('resize', o.updateBound, { passive: !0 }); var r = n(e); return M(r, 'scroll', o.updateBound, o.scrollParents), o.scrollElement = r, o.eventsEnabled = !0, o } function I() { this.state.eventsEnabled || (this.state = F(this.reference, this.options, this.state, this.scheduleUpdate)) } function R(e, t) { return A(e).removeEventListener('resize', t.updateBound), t.scrollParents.forEach(function (e) { e.removeEventListener('scroll', t.updateBound) }), t.updateBound = null, t.scrollParents = [], t.scrollElement = null, t.eventsEnabled = !1, t } function U() { this.state.eventsEnabled && (cancelAnimationFrame(this.scheduleUpdate), this.state = R(this.reference, this.state)) } function Y(e) { return '' !== e && !isNaN(parseFloat(e)) && isFinite(e) } function V(e, t) { Object.keys(t).forEach(function (o) { var n = ''; -1 !== ['width', 'height', 'top', 'right', 'bottom', 'left'].indexOf(o) && Y(t[o]) && (n = 'px'), e.style[o] = t[o] + n }) } function j(e, t) { Object.keys(t).forEach(function (o) { var n = t[o]; !1 === n ? e.removeAttribute(o) : e.setAttribute(o, t[o]) }) } function q(e, t) { var o = e.offsets, n = o.popper, i = o.reference, r = $, p = function (e) { return e }, s = r(i.width), d = r(n.width), a = -1 !== ['left', 'right'].indexOf(e.placement), l = -1 !== e.placement.indexOf('-'), f = t ? a || l || s % 2 == d % 2 ? r : Z : p, m = t ? r : p; return { left: f(1 == s % 2 && 1 == d % 2 && !l && t ? n.left - 1 : n.left), top: m(n.top), bottom: m(n.bottom), right: f(n.right) } } function K(e, t, o) { var n = D(e, function (e) { var o = e.name; return o === t }), i = !!n && e.some(function (e) { return e.name === o && e.enabled && e.order < n.order }); if (!i) { var r = '`' + t + '`'; console.warn('`' + o + '`' + ' modifier is required by ' + r + ' modifier in order to work, be sure to include it before ' + r + '!') } return i } function z(e) { return 'end' === e ? 'start' : 'start' === e ? 'end' : e } function G(e) { var t = 1 < arguments.length && void 0 !== arguments[1] && arguments[1], o = ce.indexOf(e), n = ce.slice(o + 1).concat(ce.slice(0, o)); return t ? n.reverse() : n } function _(e, t, o, n) { var i = e.match(/((?:\-|\+)?\d*\.?\d*)(.*)/), r = +i[1], p = i[2]; if (!r) return e; if (0 === p.indexOf('%')) { var s; switch (p) { case '%p': s = o; break; case '%': case '%r': default: s = n; }var d = g(s); return d[t] / 100 * r } if ('vh' === p || 'vw' === p) { var a; return a = 'vh' === p ? ee(document.documentElement.clientHeight, window.innerHeight || 0) : ee(document.documentElement.clientWidth, window.innerWidth || 0), a / 100 * r } return r } function X(e, t, o, n) { var i = [0, 0], r = -1 !== ['right', 'left'].indexOf(n), p = e.split(/(\+|\-)/).map(function (e) { return e.trim() }), s = p.indexOf(D(p, function (e) { return -1 !== e.search(/,|\s/) })); p[s] && -1 === p[s].indexOf(',') && console.warn('Offsets separated by white space(s) are deprecated, use a comma (,) instead.'); var d = /\s*,\s*|\s+/, a = -1 === s ? [p] : [p.slice(0, s).concat([p[s].split(d)[0]]), [p[s].split(d)[1]].concat(p.slice(s + 1))]; return a = a.map(function (e, n) { var i = (1 === n ? !r : r) ? 'height' : 'width', p = !1; return e.reduce(function (e, t) { return '' === e[e.length - 1] && -1 !== ['+', '-'].indexOf(t) ? (e[e.length - 1] = t, p = !0, e) : p ? (e[e.length - 1] += t, p = !1, e) : e.concat(t) }, []).map(function (e) { return _(e, i, t, o) }) }), a.forEach(function (e, t) { e.forEach(function (o, n) { Y(o) && (i[t] += o * ('-' === e[n - 1] ? -1 : 1)) }) }), i } function J(e, t) { var o, n = t.offset, i = e.placement, r = e.offsets, p = r.popper, s = r.reference, d = i.split('-')[0]; return o = Y(+n) ? [+n, 0] : X(n, p, s, d), 'left' === d ? (p.top += o[0], p.left -= o[1]) : 'right' === d ? (p.top += o[0], p.left += o[1]) : 'top' === d ? (p.left += o[0], p.top -= o[1]) : 'bottom' === d && (p.left += o[0], p.top += o[1]), e.popper = p, e } for (var Q = Math.min, Z = Math.floor, $ = Math.round, ee = Math.max, te = 'undefined' != typeof window && 'undefined' != typeof document, oe = ['Edge', 'Trident', 'Firefox'], ne = 0, ie = 0; ie < oe.length; ie += 1)if (te && 0 <= navigator.userAgent.indexOf(oe[ie])) { ne = 1; break } var i = te && window.Promise, re = i ? function (e) { var t = !1; return function () { t || (t = !0, window.Promise.resolve().then(function () { t = !1, e() })) } } : function (e) { var t = !1; return function () { t || (t = !0, setTimeout(function () { t = !1, e() }, ne)) } }, pe = te && !!(window.MSInputMethodContext && document.documentMode), se = te && /MSIE 10/.test(navigator.userAgent), de = function (e, t) { if (!(e instanceof t)) throw new TypeError('Cannot call a class as a function') }, ae = function () { function e(e, t) { for (var o, n = 0; n < t.length; n++)o = t[n], o.enumerable = o.enumerable || !1, o.configurable = !0, 'value' in o && (o.writable = !0), Object.defineProperty(e, o.key, o) } return function (t, o, n) { return o && e(t.prototype, o), n && e(t, n), t } }(), le = function (e, t, o) { return t in e ? Object.defineProperty(e, t, { value: o, enumerable: !0, configurable: !0, writable: !0 }) : e[t] = o, e }, fe = Object.assign || function (e) { for (var t, o = 1; o < arguments.length; o++)for (var n in t = arguments[o], t) Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]); return e }, me = te && /Firefox/i.test(navigator.userAgent), he = ['auto-start', 'auto', 'auto-end', 'top-start', 'top', 'top-end', 'right-start', 'right', 'right-end', 'bottom-end', 'bottom', 'bottom-start', 'left-end', 'left', 'left-start'], ce = he.slice(3), ge = { FLIP: 'flip', CLOCKWISE: 'clockwise', COUNTERCLOCKWISE: 'counterclockwise' }, ue = function () { function t(o, n) { var i = this, r = 2 < arguments.length && void 0 !== arguments[2] ? arguments[2] : {}; de(this, t), this.scheduleUpdate = function () { return requestAnimationFrame(i.update) }, this.update = re(this.update.bind(this)), this.options = fe({}, t.Defaults, r), this.state = { isDestroyed: !1, isCreated: !1, scrollParents: [] }, this.reference = o && o.jquery ? o[0] : o, this.popper = n && n.jquery ? n[0] : n, this.options.modifiers = {}, Object.keys(fe({}, t.Defaults.modifiers, r.modifiers)).forEach(function (e) { i.options.modifiers[e] = fe({}, t.Defaults.modifiers[e] || {}, r.modifiers ? r.modifiers[e] : {}) }), this.modifiers = Object.keys(this.options.modifiers).map(function (e) { return fe({ name: e }, i.options.modifiers[e]) }).sort(function (e, t) { return e.order - t.order }), this.modifiers.forEach(function (t) { t.enabled && e(t.onLoad) && t.onLoad(i.reference, i.popper, i.options, t, i.state) }), this.update(); var p = this.options.eventsEnabled; p && this.enableEventListeners(), this.state.eventsEnabled = p } return ae(t, [{ key: 'update', value: function () { return k.call(this) } }, { key: 'destroy', value: function () { return H.call(this) } }, { key: 'enableEventListeners', value: function () { return I.call(this) } }, { key: 'disableEventListeners', value: function () { return U.call(this) } }]), t }(); return ue.Utils = ('undefined' == typeof window ? global : window).PopperUtils, ue.placements = he, ue.Defaults = { placement: 'bottom', positionFixed: !1, eventsEnabled: !0, removeOnDestroy: !1, onCreate: function () { }, onUpdate: function () { }, modifiers: { shift: { order: 100, enabled: !0, fn: function (e) { var t = e.placement, o = t.split('-')[0], n = t.split('-')[1]; if (n) { var i = e.offsets, r = i.reference, p = i.popper, s = -1 !== ['bottom', 'top'].indexOf(o), d = s ? 'left' : 'top', a = s ? 'width' : 'height', l = { start: le({}, d, r[d]), end: le({}, d, r[d] + r[a] - p[a]) }; e.offsets.popper = fe({}, p, l[n]) } return e } }, offset: { order: 200, enabled: !0, fn: J, offset: 0 }, preventOverflow: { order: 300, enabled: !0, fn: function (e, t) { var o = t.boundariesElement || p(e.instance.popper); e.instance.reference === o && (o = p(o)); var n = B('transform'), i = e.instance.popper.style, r = i.top, s = i.left, d = i[n]; i.top = '', i.left = '', i[n] = ''; var a = v(e.instance.popper, e.instance.reference, t.padding, o, e.positionFixed); i.top = r, i.left = s, i[n] = d, t.boundaries = a; var l = t.priority, f = e.offsets.popper, m = { primary: function (e) { var o = f[e]; return f[e] < a[e] && !t.escapeWithReference && (o = ee(f[e], a[e])), le({}, e, o) }, secondary: function (e) { var o = 'right' === e ? 'left' : 'top', n = f[o]; return f[e] > a[e] && !t.escapeWithReference && (n = Q(f[o], a[e] - ('right' === e ? f.width : f.height))), le({}, o, n) } }; return l.forEach(function (e) { var t = -1 === ['left', 'top'].indexOf(e) ? 'secondary' : 'primary'; f = fe({}, f, m[t](e)) }), e.offsets.popper = f, e }, priority: ['left', 'right', 'top', 'bottom'], padding: 5, boundariesElement: 'scrollParent' }, keepTogether: { order: 400, enabled: !0, fn: function (e) { var t = e.offsets, o = t.popper, n = t.reference, i = e.placement.split('-')[0], r = Z, p = -1 !== ['top', 'bottom'].indexOf(i), s = p ? 'right' : 'bottom', d = p ? 'left' : 'top', a = p ? 'width' : 'height'; return o[s] < r(n[d]) && (e.offsets.popper[d] = r(n[d]) - o[a]), o[d] > r(n[s]) && (e.offsets.popper[d] = r(n[s])), e } }, arrow: { order: 500, enabled: !0, fn: function (e, o) { var n; if (!K(e.instance.modifiers, 'arrow', 'keepTogether')) return e; var i = o.element; if ('string' == typeof i) { if (i = e.instance.popper.querySelector(i), !i) return e; } else if (!e.instance.popper.contains(i)) return console.warn('WARNING: `arrow.element` must be child of its popper element!'), e; var r = e.placement.split('-')[0], p = e.offsets, s = p.popper, d = p.reference, a = -1 !== ['left', 'right'].indexOf(r), l = a ? 'height' : 'width', f = a ? 'Top' : 'Left', m = f.toLowerCase(), h = a ? 'left' : 'top', c = a ? 'bottom' : 'right', u = S(i)[l]; d[c] - u < s[m] && (e.offsets.popper[m] -= s[m] - (d[c] - u)), d[m] + u > s[c] && (e.offsets.popper[m] += d[m] + u - s[c]), e.offsets.popper = g(e.offsets.popper); var b = d[m] + d[l] / 2 - u / 2, w = t(e.instance.popper), y = parseFloat(w['margin' + f], 10), E = parseFloat(w['border' + f + 'Width'], 10), v = b - e.offsets.popper[m] - y - E; return v = ee(Q(s[l] - u, v), 0), e.arrowElement = i, e.offsets.arrow = (n = {}, le(n, m, $(v)), le(n, h, ''), n), e }, element: '[x-arrow]' }, flip: { order: 600, enabled: !0, fn: function (e, t) { if (W(e.instance.modifiers, 'inner')) return e; if (e.flipped && e.placement === e.originalPlacement) return e; var o = v(e.instance.popper, e.instance.reference, t.padding, t.boundariesElement, e.positionFixed), n = e.placement.split('-')[0], i = T(n), r = e.placement.split('-')[1] || '', p = []; switch (t.behavior) { case ge.FLIP: p = [n, i]; break; case ge.CLOCKWISE: p = G(n); break; case ge.COUNTERCLOCKWISE: p = G(n, !0); break; default: p = t.behavior; }return p.forEach(function (s, d) { if (n !== s || p.length === d + 1) return e; n = e.placement.split('-')[0], i = T(n); var a = e.offsets.popper, l = e.offsets.reference, f = Z, m = 'left' === n && f(a.right) > f(l.left) || 'right' === n && f(a.left) < f(l.right) || 'top' === n && f(a.bottom) > f(l.top) || 'bottom' === n && f(a.top) < f(l.bottom), h = f(a.left) < f(o.left), c = f(a.right) > f(o.right), g = f(a.top) < f(o.top), u = f(a.bottom) > f(o.bottom), b = 'left' === n && h || 'right' === n && c || 'top' === n && g || 'bottom' === n && u, w = -1 !== ['top', 'bottom'].indexOf(n), y = !!t.flipVariations && (w && 'start' === r && h || w && 'end' === r && c || !w && 'start' === r && g || !w && 'end' === r && u), E = !!t.flipVariationsByContent && (w && 'start' === r && c || w && 'end' === r && h || !w && 'start' === r && u || !w && 'end' === r && g), v = y || E; (m || b || v) && (e.flipped = !0, (m || b) && (n = p[d + 1]), v && (r = z(r)), e.placement = n + (r ? '-' + r : ''), e.offsets.popper = fe({}, e.offsets.popper, C(e.instance.popper, e.offsets.reference, e.placement)), e = P(e.instance.modifiers, e, 'flip')) }), e }, behavior: 'flip', padding: 5, boundariesElement: 'viewport', flipVariations: !1, flipVariationsByContent: !1 }, inner: { order: 700, enabled: !1, fn: function (e) { var t = e.placement, o = t.split('-')[0], n = e.offsets, i = n.popper, r = n.reference, p = -1 !== ['left', 'right'].indexOf(o), s = -1 === ['top', 'left'].indexOf(o); return i[p ? 'left' : 'top'] = r[o] - (s ? i[p ? 'width' : 'height'] : 0), e.placement = T(t), e.offsets.popper = g(i), e } }, hide: { order: 800, enabled: !0, fn: function (e) { if (!K(e.instance.modifiers, 'hide', 'preventOverflow')) return e; var t = e.offsets.reference, o = D(e.instance.modifiers, function (e) { return 'preventOverflow' === e.name }).boundaries; if (t.bottom < o.top || t.left > o.right || t.top > o.bottom || t.right < o.left) { if (!0 === e.hide) return e; e.hide = !0, e.attributes['x-out-of-boundaries'] = '' } else { if (!1 === e.hide) return e; e.hide = !1, e.attributes['x-out-of-boundaries'] = !1 } return e } }, computeStyle: { order: 850, enabled: !0, fn: function (e, t) { var o = t.x, n = t.y, i = e.offsets.popper, r = D(e.instance.modifiers, function (e) { return 'applyStyle' === e.name }).gpuAcceleration; void 0 !== r && console.warn('WARNING: `gpuAcceleration` option moved to `computeStyle` modifier and will not be supported in future versions of Popper.js!'); var s, d, a = void 0 === r ? t.gpuAcceleration : r, l = p(e.instance.popper), f = u(l), m = { position: i.position }, h = q(e, 2 > window.devicePixelRatio || !me), c = 'bottom' === o ? 'top' : 'bottom', g = 'right' === n ? 'left' : 'right', b = B('transform'); if (d = 'bottom' == c ? 'HTML' === l.nodeName ? -l.clientHeight + h.bottom : -f.height + h.bottom : h.top, s = 'right' == g ? 'HTML' === l.nodeName ? -l.clientWidth + h.right : -f.width + h.right : h.left, a && b) m[b] = 'translate3d(' + s + 'px, ' + d + 'px, 0)', m[c] = 0, m[g] = 0, m.willChange = 'transform'; else { var w = 'bottom' == c ? -1 : 1, y = 'right' == g ? -1 : 1; m[c] = d * w, m[g] = s * y, m.willChange = c + ', ' + g } var E = { "x-placement": e.placement }; return e.attributes = fe({}, E, e.attributes), e.styles = fe({}, m, e.styles), e.arrowStyles = fe({}, e.offsets.arrow, e.arrowStyles), e }, gpuAcceleration: !0, x: 'bottom', y: 'right' }, applyStyle: { order: 900, enabled: !0, fn: function (e) { return V(e.instance.popper, e.styles), j(e.instance.popper, e.attributes), e.arrowElement && Object.keys(e.arrowStyles).length && V(e.arrowElement, e.arrowStyles), e }, onLoad: function (e, t, o, n, i) { var r = L(i, t, e, o.positionFixed), p = O(o.placement, r, t, e, o.modifiers.flip.boundariesElement, o.modifiers.flip.padding); return t.setAttribute('x-placement', p), V(t, { position: o.positionFixed ? 'fixed' : 'absolute' }), o }, gpuAcceleration: void 0 } } }, ue });
//# sourceMappingURL=popper.min.js.map


// 2) https://unpkg.com/tippy.js@4

https://unpkg.com/tippy.js@4.3.5/umd/index.all.min.js
!function (t, e) { "object" == typeof exports && "undefined" != typeof module ? module.exports = e(require("popper.js")) : "function" == typeof define && define.amd ? define(["popper.js"], e) : (t = t || self).tippy = e(t.Popper) }(this, function (t) { "use strict"; t = t && t.hasOwnProperty("default") ? t.default : t; function e() { return (e = Object.assign || function (t) { for (var e = 1; e < arguments.length; e++) { var a = arguments[e]; for (var r in a) Object.prototype.hasOwnProperty.call(a, r) && (t[r] = a[r]) } return t }).apply(this, arguments) } var a = "undefined" != typeof window && "undefined" != typeof document, r = a ? navigator.userAgent : "", n = /MSIE |Trident\//.test(r), i = /UCBrowser\//.test(r), o = a && /iPhone|iPad|iPod/.test(navigator.platform) && !window.MSStream, p = { a11y: !0, allowHTML: !0, animateFill: !0, animation: "shift-away", appendTo: function () { return document.body }, aria: "describedby", arrow: !1, arrowType: "sharp", boundary: "scrollParent", content: "", delay: 0, distance: 10, duration: [325, 275], flip: !0, flipBehavior: "flip", flipOnUpdate: !1, followCursor: !1, hideOnClick: !0, ignoreAttributes: !1, inertia: !1, interactive: !1, interactiveBorder: 2, interactiveDebounce: 0, lazy: !0, maxWidth: 350, multiple: !1, offset: 0, onHidden: function () { }, onHide: function () { }, onMount: function () { }, onShow: function () { }, onShown: function () { }, onTrigger: function () { }, placement: "top", popperOptions: {}, role: "tooltip", showOnInit: !1, size: "regular", sticky: !1, target: "", theme: "dark", touch: !0, touchHold: !1, trigger: "mouseenter focus", triggerTarget: null, updateDuration: 0, wait: null, zIndex: 9999 }, s = ["arrow", "arrowType", "boundary", "distance", "flip", "flipBehavior", "flipOnUpdate", "offset", "placement", "popperOptions"], c = a ? Element.prototype : {}, l = c.matches || c.matchesSelector || c.webkitMatchesSelector || c.mozMatchesSelector || c.msMatchesSelector; function d(t) { return [].slice.call(t) } function f(t, e) { return m(t, function (t) { return l.call(t, e) }) } function m(t, e) { for (; t;) { if (e(t)) return t; t = t.parentElement } return null } var u = { passive: !0 }, b = 4, y = "x-placement", v = "x-out-of-boundaries", h = "tippy-iOS", x = "tippy-active", g = "tippy-popper", w = "tippy-tooltip", k = "tippy-content", A = "tippy-backdrop", E = "tippy-arrow", C = "tippy-roundarrow", L = ".".concat(g), X = ".".concat(w), Y = ".".concat(k), T = ".".concat(A), I = ".".concat(E), S = ".".concat(C), O = !1; function z() { O || (O = !0, o && document.body.classList.add(h), window.performance && document.addEventListener("mousemove", H)) } var M = 0; function H() { var t = performance.now(); t - M < 20 && (O = !1, document.removeEventListener("mousemove", H), o || document.body.classList.remove(h)), M = t } function V() { var t = document.activeElement; t && t.blur && t._tippy && t.blur() } var _ = Object.keys(p); function N(t, e) { return {}.hasOwnProperty.call(t, e) } function P(t, e, a) { if (Array.isArray(t)) { var r = t[e]; return null == r ? a : r } return t } function D(t, e) { return 0 === e ? t : function (r) { clearTimeout(a), a = setTimeout(function () { t(r) }, e) }; var a } function q(t, e) { return t && t.modifiers && t.modifiers[e] } function B(t, e) { return t.indexOf(e) > -1 } function F(t) { return t instanceof Element } function j(t) { return !(!t || !N(t, "isVirtual")) || F(t) } function U(t, e) { return "function" == typeof t ? t.apply(null, e) : t } function W(t, e) { t.filter(function (t) { return "flip" === t.name })[0].enabled = e } function R() { return document.createElement("div") } function J(t, e) { t.forEach(function (t) { t && (t.style.transitionDuration = "".concat(e, "ms")) }) } function G(t, e) { t.forEach(function (t) { t && t.setAttribute("data-state", e) }) } function K(t, a) { var r = e({}, a, { content: U(a.content, [t]) }, a.ignoreAttributes ? {} : function (t) { return _.reduce(function (e, a) { var r = (t.getAttribute("data-tippy-".concat(a)) || "").trim(); if (!r) return e; if ("content" === a) e[a] = r; else try { e[a] = JSON.parse(r) } catch (t) { e[a] = r } return e }, {}) }(t)); return (r.arrow || i) && (r.animateFill = !1), r } function Q(t, e) { Object.keys(t).forEach(function (t) { if (!N(e, t)) throw new Error("[tippy]: `".concat(t, "` is not a valid option")) }) } function Z(t, e) { t.innerHTML = F(e) ? e.innerHTML : e } function $(t, e) { if (F(e.content)) Z(t, ""), t.appendChild(e.content); else if ("function" != typeof e.content) { t[e.allowHTML ? "innerHTML" : "textContent"] = e.content } } function tt(t) { return { tooltip: t.querySelector(X), backdrop: t.querySelector(T), content: t.querySelector(Y), arrow: t.querySelector(I) || t.querySelector(S) } } function et(t) { t.setAttribute("data-inertia", "") } function at(t) { var e = R(); return "round" === t ? (e.className = C, Z(e, '<svg viewBox="0 0 18 7" xmlns="http://www.w3.org/2000/svg"><path d="M0 7s2.021-.015 5.253-4.218C6.584 1.051 7.797.007 9 0c1.203-.007 2.416 1.035 3.761 2.782C16.012 7.005 18 7 18 7H0z"/></svg>')) : e.className = E, e } function rt() { var t = R(); return t.className = A, t.setAttribute("data-state", "hidden"), t } function nt(t, e) { t.setAttribute("tabindex", "-1"), e.setAttribute("data-interactive", "") } function it(t, e, a) { var r = i && void 0 !== document.body.style.webkitTransition ? "webkitTransitionEnd" : "transitionend"; t[e + "EventListener"](r, a) } function ot(t) { var e = t.getAttribute(y); return e ? e.split("-")[0] : "" } function pt(t, e, a) { a.split(" ").forEach(function (a) { t.classList[e](a + "-theme") }) } function st(t, e) { var a = R(); a.className = g, a.id = "tippy-".concat(t), a.style.zIndex = "" + e.zIndex, a.style.position = "absolute", a.style.top = "0", a.style.left = "0", e.role && a.setAttribute("role", e.role); var r = R(); r.className = w, r.style.maxWidth = e.maxWidth + ("number" == typeof e.maxWidth ? "px" : ""), r.setAttribute("data-size", e.size), r.setAttribute("data-animation", e.animation), r.setAttribute("data-state", "hidden"), pt(r, "add", e.theme); var n = R(); return n.className = k, n.setAttribute("data-state", "hidden"), e.interactive && nt(a, r), e.arrow && r.appendChild(at(e.arrowType)), e.animateFill && (r.appendChild(rt()), r.setAttribute("data-animatefill", "")), e.inertia && et(r), $(n, e), r.appendChild(n), a.appendChild(r), a } function ct(t, e, a) { var r = tt(t), n = r.tooltip, i = r.content, o = r.backdrop, p = r.arrow; t.style.zIndex = "" + a.zIndex, n.setAttribute("data-size", a.size), n.setAttribute("data-animation", a.animation), n.style.maxWidth = a.maxWidth + ("number" == typeof a.maxWidth ? "px" : ""), a.role ? t.setAttribute("role", a.role) : t.removeAttribute("role"), e.content !== a.content && $(i, a), !e.animateFill && a.animateFill ? (n.appendChild(rt()), n.setAttribute("data-animatefill", "")) : e.animateFill && !a.animateFill && (n.removeChild(o), n.removeAttribute("data-animatefill")), !e.arrow && a.arrow ? n.appendChild(at(a.arrowType)) : e.arrow && !a.arrow && n.removeChild(p), e.arrow && a.arrow && e.arrowType !== a.arrowType && n.replaceChild(at(a.arrowType), p), !e.interactive && a.interactive ? nt(t, n) : e.interactive && !a.interactive && function (t, e) { t.removeAttribute("tabindex"), e.removeAttribute("data-interactive") }(t, n), !e.inertia && a.inertia ? et(n) : e.inertia && !a.inertia && function (t) { t.removeAttribute("data-inertia") }(n), e.theme !== a.theme && (pt(n, "remove", e.theme), pt(n, "add", a.theme)) } var lt = 1, dt = []; function ft(a, r) { var i, o, c, h, g, w = K(a, r); if (!w.multiple && a._tippy) return null; var k, A, E, C, X, Y = !1, T = !1, I = !1, S = !1, z = [], M = D(ht, w.interactiveDebounce), H = lt++, V = st(H, w), _ = tt(V), j = { id: H, reference: a, popper: V, popperChildren: _, popperInstance: null, props: w, state: { isEnabled: !0, isVisible: !1, isDestroyed: !1, isMounted: !1, isShown: !1 }, clearDelayTimeouts: Tt, set: It, setContent: function (t) { It({ content: t }) }, show: St, hide: Ot, enable: function () { j.state.isEnabled = !0 }, disable: function () { j.state.isEnabled = !1 }, destroy: function (t) { if (j.state.isDestroyed) return; T = !0, j.state.isMounted && Ot(0); bt(), delete a._tippy; var e = j.props.target; e && t && F(a) && d(a.querySelectorAll(e)).forEach(function (t) { t._tippy && t._tippy.destroy() }); j.popperInstance && j.popperInstance.destroy(); T = !1, j.state.isDestroyed = !0 } }; return a._tippy = j, V._tippy = j, ut(), w.lazy || Ct(), w.showOnInit && Lt(), !w.a11y || w.target || (!F(X = $()) || l.call(X, "a[href],area[href],button,details,input,textarea,select,iframe,[tabindex]") && !X.hasAttribute("disabled")) || $().setAttribute("tabindex", "0"), V.addEventListener("mouseenter", function (t) { j.props.interactive && j.state.isVisible && "mouseenter" === i && Lt(t, !0) }), V.addEventListener("mouseleave", function () { j.props.interactive && "mouseenter" === i && document.addEventListener("mousemove", M) }), j; function R() { document.removeEventListener("mousemove", yt) } function Z() { document.body.removeEventListener("mouseleave", Xt), document.removeEventListener("mousemove", M), dt = dt.filter(function (t) { return t !== M }) } function $() { return j.props.triggerTarget || a } function et() { document.addEventListener("click", Yt, !0) } function at() { document.removeEventListener("click", Yt, !0) } function rt() { return [j.popperChildren.tooltip, j.popperChildren.backdrop, j.popperChildren.content] } function nt() { var t = j.props.followCursor; return t && "focus" !== i || O && "initial" === t } function pt(t, e) { var a = j.popperChildren.tooltip; function r(t) { t.target === a && (it(a, "remove", r), e()) } if (0 === t) return e(); it(a, "remove", E), it(a, "add", r), E = r } function mt(t, e) { var a = arguments.length > 2 && void 0 !== arguments[2] && arguments[2]; $().addEventListener(t, e, a), z.push({ eventType: t, handler: e, options: a }) } function ut() { j.props.touchHold && !j.props.target && (mt("touchstart", vt, u), mt("touchend", xt, u)), j.props.trigger.trim().split(" ").forEach(function (t) { if ("manual" !== t) if (j.props.target) switch (t) { case "mouseenter": mt("mouseover", wt), mt("mouseout", kt); break; case "focus": mt("focusin", wt), mt("focusout", kt); break; case "click": mt(t, wt) } else switch (mt(t, vt), t) { case "mouseenter": mt("mouseleave", xt); break; case "focus": mt(n ? "focusout" : "blur", gt) } }) } function bt() { z.forEach(function (t) { var e = t.eventType, a = t.handler, r = t.options; $().removeEventListener(e, a, r) }), z = [] } function yt(t) { var r = o = t, n = r.clientX, i = r.clientY; if (C) { var p = m(t.target, function (t) { return t === a }), s = a.getBoundingClientRect(), c = j.props.followCursor, l = "horizontal" === c, d = "vertical" === c, f = B(["top", "bottom"], ot(V)), u = V.getAttribute(y), b = !!u && !!u.split("-")[1], v = f ? V.offsetWidth : V.offsetHeight, h = v / 2, x = f ? 0 : b ? v : h, g = f ? b ? v : h : 0; !p && j.props.interactive || (j.popperInstance.reference = e({}, j.popperInstance.reference, { referenceNode: a, clientWidth: 0, clientHeight: 0, getBoundingClientRect: function () { return { width: f ? v : 0, height: f ? 0 : v, top: (l ? s.top : i) - x, bottom: (l ? s.bottom : i) + x, left: (d ? s.left : n) - g, right: (d ? s.right : n) + g } } }), j.popperInstance.update()), "initial" === c && j.state.isVisible && R() } } function vt(t) { j.state.isEnabled && !At(t) && (j.state.isVisible || (i = t.type, t instanceof MouseEvent && (o = t, dt.forEach(function (e) { return e(t) }))), "click" === t.type && !1 !== j.props.hideOnClick && j.state.isVisible ? Xt() : Lt(t)) } function ht(t) { var e = f(t.target, L) === V, r = m(t.target, function (t) { return t === a }); e || r || function (t, e, a, r) { if (!t) return !0; var n = a.clientX, i = a.clientY, o = r.interactiveBorder, p = r.distance, s = e.top - i > ("top" === t ? o + p : o), c = i - e.bottom > ("bottom" === t ? o + p : o), l = e.left - n > ("left" === t ? o + p : o), d = n - e.right > ("right" === t ? o + p : o); return s || c || l || d }(ot(V), V.getBoundingClientRect(), t, j.props) && (Z(), Xt()) } function xt(t) { if (!At(t)) return j.props.interactive ? (document.body.addEventListener("mouseleave", Xt), document.addEventListener("mousemove", M), void dt.push(M)) : void Xt() } function gt(t) { t.target === $() && (j.props.interactive && t.relatedTarget && V.contains(t.relatedTarget) || Xt()) } function wt(t) { f(t.target, j.props.target) && Lt(t) } function kt(t) { f(t.target, j.props.target) && Xt() } function At(t) { var e = "ontouchstart" in window, a = B(t.type, "touch"), r = j.props.touchHold; return e && O && r && !a || O && !r && a } function Et() { !S && A && (S = !0, function (t) { t.offsetHeight }(V), A()) } function Ct() { var r = j.props.popperOptions, n = j.popperChildren, i = n.tooltip, o = n.arrow, p = q(r, "preventOverflow"); function s(t) { j.props.flip && !j.props.flipOnUpdate && (t.flipped && (j.popperInstance.options.placement = t.placement), W(j.popperInstance.modifiers, !1)), i.setAttribute(y, t.placement), !1 !== t.attributes[v] ? i.setAttribute(v, "") : i.removeAttribute(v), k && k !== t.placement && I && (i.style.transition = "none", requestAnimationFrame(function () { i.style.transition = "" })), k = t.placement, I = j.state.isVisible; var a = ot(V), r = i.style; r.top = r.bottom = r.left = r.right = "", r[a] = -(j.props.distance - 10) + "px"; var n = p && void 0 !== p.padding ? p.padding : b, o = "number" == typeof n, s = e({ top: o ? n : n.top, bottom: o ? n : n.bottom, left: o ? n : n.left, right: o ? n : n.right }, !o && n); s[a] = o ? n + j.props.distance : (n[a] || 0) + j.props.distance, j.popperInstance.modifiers.filter(function (t) { return "preventOverflow" === t.name })[0].padding = s, C = s } var c = e({ eventsEnabled: !1, placement: j.props.placement }, r, { modifiers: e({}, r ? r.modifiers : {}, { preventOverflow: e({ boundariesElement: j.props.boundary, padding: b }, p), arrow: e({ element: o, enabled: !!o }, q(r, "arrow")), flip: e({ enabled: j.props.flip, padding: j.props.distance + b, behavior: j.props.flipBehavior }, q(r, "flip")), offset: e({ offset: j.props.offset }, q(r, "offset")) }), onCreate: function (t) { s(t), Et(), r && r.onCreate && r.onCreate(t) }, onUpdate: function (t) { s(t), Et(), r && r.onUpdate && r.onUpdate(t) } }); j.popperInstance = new t(a, V, c) } function Lt(t, a) { if (Tt(), !j.state.isVisible) { if (j.props.target) return function (t) { if (t) { var a = f(t.target, j.props.target); a && !a._tippy && ft(a, e({}, j.props, { content: U(r.content, [a]), appendTo: r.appendTo, target: "", showOnInit: !0 })) } }(t); if (Y = !0, t && !a && j.props.onTrigger(j, t), j.props.wait) return j.props.wait(j, t); nt() && !j.state.isMounted && (j.popperInstance || Ct(), document.addEventListener("mousemove", yt)), et(); var n = P(j.props.delay, 0, p.delay); n ? c = setTimeout(function () { St() }, n) : St() } } function Xt() { if (Tt(), !j.state.isVisible) return R(), void at(); Y = !1; var t = P(j.props.delay, 1, p.delay); t ? h = setTimeout(function () { j.state.isVisible && Ot() }, t) : g = requestAnimationFrame(function () { Ot() }) } function Yt(t) { if (!j.props.interactive || !V.contains(t.target)) { if ($().contains(t.target)) { if (O) return; if (j.state.isVisible && B(j.props.trigger, "click")) return } !0 === j.props.hideOnClick && (Tt(), Ot()) } } function Tt() { clearTimeout(c), clearTimeout(h), cancelAnimationFrame(g) } function It(t) { Q(t = t || {}, p), bt(); var r = j.props, n = K(a, e({}, j.props, {}, t, { ignoreAttributes: !0 })); n.ignoreAttributes = N(t, "ignoreAttributes") ? t.ignoreAttributes || !1 : r.ignoreAttributes, j.props = n, ut(), Z(), M = D(ht, n.interactiveDebounce), ct(V, r, n), j.popperChildren = tt(V), j.popperInstance && (s.some(function (e) { return N(t, e) && t[e] !== r[e] }) ? (j.popperInstance.destroy(), Ct(), j.state.isVisible && j.popperInstance.enableEventListeners(), j.props.followCursor && o && yt(o)) : j.popperInstance.update()) } function St() { var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : P(j.props.duration, 0, p.duration[1]); if (!j.state.isDestroyed && j.state.isEnabled && (!O || j.props.touch) && !$().hasAttribute("disabled") && !1 !== j.props.onShow(j)) { et(), V.style.visibility = "visible", j.state.isVisible = !0, j.props.interactive && $().classList.add(x); var e = rt(); J(e.concat(V), 0), A = function () { if (j.state.isVisible) { var r = nt(); r && o ? yt(o) : r || j.popperInstance.update(), j.popperChildren.backdrop && (j.popperChildren.content.style.transitionDelay = Math.round(t / 12) + "ms"), j.props.sticky && function () { J([V], n ? 0 : j.props.updateDuration); var t = a.getBoundingClientRect(); !function e() { var r = a.getBoundingClientRect(); t.top === r.top && t.right === r.right && t.bottom === r.bottom && t.left === r.left || j.popperInstance.scheduleUpdate(), t = r, j.state.isMounted && requestAnimationFrame(e) }() }(), J([V], j.props.updateDuration), J(e, t), G(e, "visible"), function (t, e) { pt(t, e) }(t, function () { j.props.aria && $().setAttribute("aria-".concat(j.props.aria), V.id), j.props.onShown(j), j.state.isShown = !0 }) } }, function () { S = !1; var t = nt(); j.popperInstance ? (W(j.popperInstance.modifiers, j.props.flip), t || (j.popperInstance.reference = a, j.popperInstance.enableEventListeners()), j.popperInstance.scheduleUpdate()) : (Ct(), t || j.popperInstance.enableEventListeners()); var e = j.props.appendTo, r = "parent" === e ? a.parentNode : U(e, [a]); r.contains(V) || (r.appendChild(V), j.props.onMount(j), j.state.isMounted = !0) }() } } function Ot() { var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : P(j.props.duration, 1, p.duration[1]); if (!j.state.isDestroyed && (j.state.isEnabled || T) && (!1 !== j.props.onHide(j) || T)) { at(), V.style.visibility = "hidden", j.state.isVisible = !1, j.state.isShown = !1, I = !1, j.props.interactive && $().classList.remove(x); var e = rt(); J(e, t), G(e, "hidden"), function (t, e) { pt(t, function () { !j.state.isVisible && V.parentNode && V.parentNode.contains(V) && e() }) }(t, function () { Y || R(), j.props.aria && $().removeAttribute("aria-".concat(j.props.aria)), j.popperInstance.disableEventListeners(), j.popperInstance.options.placement = j.props.placement, V.parentNode.removeChild(V), j.props.onHidden(j), j.state.isMounted = !1 }) } } } var mt = !1; function ut(t, a) { Q(a || {}, p), mt || (document.addEventListener("touchstart", z, u), window.addEventListener("blur", V), mt = !0); var r, n = e({}, p, {}, a); r = t, "[object Object]" !== {}.toString.call(r) || r.addEventListener || function (t) { var e = { isVirtual: !0, attributes: t.attributes || {}, contains: function () { }, setAttribute: function (e, a) { t.attributes[e] = a }, getAttribute: function (e) { return t.attributes[e] }, removeAttribute: function (e) { delete t.attributes[e] }, hasAttribute: function (e) { return e in t.attributes }, addEventListener: function () { }, removeEventListener: function () { }, classList: { classNames: {}, add: function (e) { t.classList.classNames[e] = !0 }, remove: function (e) { delete t.classList.classNames[e] }, contains: function (e) { return e in t.classList.classNames } } }; for (var a in e) t[a] = e[a] }(t); var i = function (t) { if (j(t)) return [t]; if (t instanceof NodeList) return d(t); if (Array.isArray(t)) return t; try { return d(document.querySelectorAll(t)) } catch (t) { return [] } }(t).reduce(function (t, e) { var a = e && ft(e, n); return a && t.push(a), t }, []); return j(t) ? i[0] : i } return ut.version = "4.3.5", ut.defaults = p, ut.setDefaults = function (t) { Object.keys(t).forEach(function (e) { p[e] = t[e] }) }, ut.hideAll = function () { var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}, e = t.exclude, a = t.duration; d(document.querySelectorAll(L)).forEach(function (t) { var r, n = t._tippy; if (n) { var i = !1; e && (i = (r = e)._tippy && !l.call(r, L) ? n.reference === e : t === e.popper), i || n.hide(a) } }) }, ut.group = function (t) { var a = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {}, r = a.delay, n = void 0 === r ? t[0].props.delay : r, i = a.duration, o = void 0 === i ? 0 : i, p = !1; function s(t) { p = t, f() } function c(e) { e._originalProps.onShow(e), t.forEach(function (t) { t.set({ duration: o }), t.state.isVisible && t.hide() }), s(!0) } function l(t) { t._originalProps.onHide(t), s(!1) } function d(t) { t._originalProps.onShown(t), t.set({ duration: t._originalProps.duration }) } function f() { t.forEach(function (t) { t.set({ onShow: c, onShown: d, onHide: l, delay: p ? [0, Array.isArray(n) ? n[1] : n] : n, duration: p ? o : t._originalProps.duration }) }) } t.forEach(function (t) { t._originalProps ? t.set(t._originalProps) : t._originalProps = e({}, t.props) }), f() }, a && setTimeout(function () { d(document.querySelectorAll("[data-tippy]")).forEach(function (t) { var e = t.getAttribute("data-tippy"); e && ut(t, { content: e }) }) }), function (t) { if (a) { var e = document.createElement("style"); e.type = "text/css", e.textContent = t, e.setAttribute("data-tippy-stylesheet", ""); var r = document.head, n = r.querySelector("style,link"); n ? r.insertBefore(e, n) : r.appendChild(e) } }('.tippy-iOS{cursor:pointer!important;-webkit-tap-highlight-color:transparent}.tippy-popper{transition-timing-function:cubic-bezier(.165,.84,.44,1);max-width:calc(100% - 8px);pointer-events:none;outline:0}.tippy-popper[x-placement^=top] .tippy-backdrop{border-radius:40% 40% 0 0}.tippy-popper[x-placement^=top] .tippy-roundarrow{bottom:-7px;bottom:-6.5px;-webkit-transform-origin:50% 0;transform-origin:50% 0;margin:0 3px}.tippy-popper[x-placement^=top] .tippy-roundarrow svg{position:absolute;left:0;-webkit-transform:rotate(180deg);transform:rotate(180deg)}.tippy-popper[x-placement^=top] .tippy-arrow{border-top:8px solid #333;border-right:8px solid transparent;border-left:8px solid transparent;bottom:-7px;margin:0 3px;-webkit-transform-origin:50% 0;transform-origin:50% 0}.tippy-popper[x-placement^=top] .tippy-backdrop{-webkit-transform-origin:0 25%;transform-origin:0 25%}.tippy-popper[x-placement^=top] .tippy-backdrop[data-state=visible]{-webkit-transform:scale(1) translate(-50%,-55%);transform:scale(1) translate(-50%,-55%)}.tippy-popper[x-placement^=top] .tippy-backdrop[data-state=hidden]{-webkit-transform:scale(.2) translate(-50%,-45%);transform:scale(.2) translate(-50%,-45%);opacity:0}.tippy-popper[x-placement^=top] [data-animation=shift-toward][data-state=visible]{-webkit-transform:translateY(-10px);transform:translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=shift-toward][data-state=hidden]{opacity:0;-webkit-transform:translateY(-20px);transform:translateY(-20px)}.tippy-popper[x-placement^=top] [data-animation=perspective]{-webkit-transform-origin:bottom;transform-origin:bottom}.tippy-popper[x-placement^=top] [data-animation=perspective][data-state=visible]{-webkit-transform:perspective(700px) translateY(-10px);transform:perspective(700px) translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=perspective][data-state=hidden]{opacity:0;-webkit-transform:perspective(700px) rotateX(60deg);transform:perspective(700px) rotateX(60deg)}.tippy-popper[x-placement^=top] [data-animation=fade][data-state=visible]{-webkit-transform:translateY(-10px);transform:translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=fade][data-state=hidden]{opacity:0;-webkit-transform:translateY(-10px);transform:translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=shift-away][data-state=visible]{-webkit-transform:translateY(-10px);transform:translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=shift-away][data-state=hidden]{opacity:0}.tippy-popper[x-placement^=top] [data-animation=scale]{-webkit-transform-origin:bottom;transform-origin:bottom}.tippy-popper[x-placement^=top] [data-animation=scale][data-state=visible]{-webkit-transform:translateY(-10px);transform:translateY(-10px)}.tippy-popper[x-placement^=top] [data-animation=scale][data-state=hidden]{opacity:0;-webkit-transform:translateY(-10px) scale(.5);transform:translateY(-10px) scale(.5)}.tippy-popper[x-placement^=bottom] .tippy-backdrop{border-radius:0 0 30% 30%}.tippy-popper[x-placement^=bottom] .tippy-roundarrow{top:-7px;-webkit-transform-origin:50% 100%;transform-origin:50% 100%;margin:0 3px}.tippy-popper[x-placement^=bottom] .tippy-roundarrow svg{position:absolute;left:0}.tippy-popper[x-placement^=bottom] .tippy-arrow{border-bottom:8px solid #333;border-right:8px solid transparent;border-left:8px solid transparent;top:-7px;margin:0 3px;-webkit-transform-origin:50% 100%;transform-origin:50% 100%}.tippy-popper[x-placement^=bottom] .tippy-backdrop{-webkit-transform-origin:0 -50%;transform-origin:0 -50%}.tippy-popper[x-placement^=bottom] .tippy-backdrop[data-state=visible]{-webkit-transform:scale(1) translate(-50%,-45%);transform:scale(1) translate(-50%,-45%)}.tippy-popper[x-placement^=bottom] .tippy-backdrop[data-state=hidden]{-webkit-transform:scale(.2) translate(-50%);transform:scale(.2) translate(-50%);opacity:0}.tippy-popper[x-placement^=bottom] [data-animation=shift-toward][data-state=visible]{-webkit-transform:translateY(10px);transform:translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=shift-toward][data-state=hidden]{opacity:0;-webkit-transform:translateY(20px);transform:translateY(20px)}.tippy-popper[x-placement^=bottom] [data-animation=perspective]{-webkit-transform-origin:top;transform-origin:top}.tippy-popper[x-placement^=bottom] [data-animation=perspective][data-state=visible]{-webkit-transform:perspective(700px) translateY(10px);transform:perspective(700px) translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=perspective][data-state=hidden]{opacity:0;-webkit-transform:perspective(700px) rotateX(-60deg);transform:perspective(700px) rotateX(-60deg)}.tippy-popper[x-placement^=bottom] [data-animation=fade][data-state=visible]{-webkit-transform:translateY(10px);transform:translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=fade][data-state=hidden]{opacity:0;-webkit-transform:translateY(10px);transform:translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=shift-away][data-state=visible]{-webkit-transform:translateY(10px);transform:translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=shift-away][data-state=hidden]{opacity:0}.tippy-popper[x-placement^=bottom] [data-animation=scale]{-webkit-transform-origin:top;transform-origin:top}.tippy-popper[x-placement^=bottom] [data-animation=scale][data-state=visible]{-webkit-transform:translateY(10px);transform:translateY(10px)}.tippy-popper[x-placement^=bottom] [data-animation=scale][data-state=hidden]{opacity:0;-webkit-transform:translateY(10px) scale(.5);transform:translateY(10px) scale(.5)}.tippy-popper[x-placement^=left] .tippy-backdrop{border-radius:50% 0 0 50%}.tippy-popper[x-placement^=left] .tippy-roundarrow{right:-12px;-webkit-transform-origin:33.33333333% 50%;transform-origin:33.33333333% 50%;margin:3px 0}.tippy-popper[x-placement^=left] .tippy-roundarrow svg{position:absolute;left:0;-webkit-transform:rotate(90deg);transform:rotate(90deg)}.tippy-popper[x-placement^=left] .tippy-arrow{border-left:8px solid #333;border-top:8px solid transparent;border-bottom:8px solid transparent;right:-7px;margin:3px 0;-webkit-transform-origin:0 50%;transform-origin:0 50%}.tippy-popper[x-placement^=left] .tippy-backdrop{-webkit-transform-origin:50% 0;transform-origin:50% 0}.tippy-popper[x-placement^=left] .tippy-backdrop[data-state=visible]{-webkit-transform:scale(1) translate(-50%,-50%);transform:scale(1) translate(-50%,-50%)}.tippy-popper[x-placement^=left] .tippy-backdrop[data-state=hidden]{-webkit-transform:scale(.2) translate(-75%,-50%);transform:scale(.2) translate(-75%,-50%);opacity:0}.tippy-popper[x-placement^=left] [data-animation=shift-toward][data-state=visible]{-webkit-transform:translateX(-10px);transform:translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=shift-toward][data-state=hidden]{opacity:0;-webkit-transform:translateX(-20px);transform:translateX(-20px)}.tippy-popper[x-placement^=left] [data-animation=perspective]{-webkit-transform-origin:right;transform-origin:right}.tippy-popper[x-placement^=left] [data-animation=perspective][data-state=visible]{-webkit-transform:perspective(700px) translateX(-10px);transform:perspective(700px) translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=perspective][data-state=hidden]{opacity:0;-webkit-transform:perspective(700px) rotateY(-60deg);transform:perspective(700px) rotateY(-60deg)}.tippy-popper[x-placement^=left] [data-animation=fade][data-state=visible]{-webkit-transform:translateX(-10px);transform:translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=fade][data-state=hidden]{opacity:0;-webkit-transform:translateX(-10px);transform:translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=shift-away][data-state=visible]{-webkit-transform:translateX(-10px);transform:translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=shift-away][data-state=hidden]{opacity:0}.tippy-popper[x-placement^=left] [data-animation=scale]{-webkit-transform-origin:right;transform-origin:right}.tippy-popper[x-placement^=left] [data-animation=scale][data-state=visible]{-webkit-transform:translateX(-10px);transform:translateX(-10px)}.tippy-popper[x-placement^=left] [data-animation=scale][data-state=hidden]{opacity:0;-webkit-transform:translateX(-10px) scale(.5);transform:translateX(-10px) scale(.5)}.tippy-popper[x-placement^=right] .tippy-backdrop{border-radius:0 50% 50% 0}.tippy-popper[x-placement^=right] .tippy-roundarrow{left:-12px;-webkit-transform-origin:66.66666666% 50%;transform-origin:66.66666666% 50%;margin:3px 0}.tippy-popper[x-placement^=right] .tippy-roundarrow svg{position:absolute;left:0;-webkit-transform:rotate(-90deg);transform:rotate(-90deg)}.tippy-popper[x-placement^=right] .tippy-arrow{border-right:8px solid #333;border-top:8px solid transparent;border-bottom:8px solid transparent;left:-7px;margin:3px 0;-webkit-transform-origin:100% 50%;transform-origin:100% 50%}.tippy-popper[x-placement^=right] .tippy-backdrop{-webkit-transform-origin:-50% 0;transform-origin:-50% 0}.tippy-popper[x-placement^=right] .tippy-backdrop[data-state=visible]{-webkit-transform:scale(1) translate(-50%,-50%);transform:scale(1) translate(-50%,-50%)}.tippy-popper[x-placement^=right] .tippy-backdrop[data-state=hidden]{-webkit-transform:scale(.2) translate(-25%,-50%);transform:scale(.2) translate(-25%,-50%);opacity:0}.tippy-popper[x-placement^=right] [data-animation=shift-toward][data-state=visible]{-webkit-transform:translateX(10px);transform:translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=shift-toward][data-state=hidden]{opacity:0;-webkit-transform:translateX(20px);transform:translateX(20px)}.tippy-popper[x-placement^=right] [data-animation=perspective]{-webkit-transform-origin:left;transform-origin:left}.tippy-popper[x-placement^=right] [data-animation=perspective][data-state=visible]{-webkit-transform:perspective(700px) translateX(10px);transform:perspective(700px) translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=perspective][data-state=hidden]{opacity:0;-webkit-transform:perspective(700px) rotateY(60deg);transform:perspective(700px) rotateY(60deg)}.tippy-popper[x-placement^=right] [data-animation=fade][data-state=visible]{-webkit-transform:translateX(10px);transform:translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=fade][data-state=hidden]{opacity:0;-webkit-transform:translateX(10px);transform:translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=shift-away][data-state=visible]{-webkit-transform:translateX(10px);transform:translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=shift-away][data-state=hidden]{opacity:0}.tippy-popper[x-placement^=right] [data-animation=scale]{-webkit-transform-origin:left;transform-origin:left}.tippy-popper[x-placement^=right] [data-animation=scale][data-state=visible]{-webkit-transform:translateX(10px);transform:translateX(10px)}.tippy-popper[x-placement^=right] [data-animation=scale][data-state=hidden]{opacity:0;-webkit-transform:translateX(10px) scale(.5);transform:translateX(10px) scale(.5)}.tippy-tooltip{position:relative;color:#fff;border-radius:.25rem;font-size:.875rem;padding:.3125rem .5625rem;line-height:1.4;text-align:center;background-color:#333}.tippy-tooltip[data-size=small]{padding:.1875rem .375rem;font-size:.75rem}.tippy-tooltip[data-size=large]{padding:.375rem .75rem;font-size:1rem}.tippy-tooltip[data-animatefill]{overflow:hidden;background-color:initial}.tippy-tooltip[data-interactive],.tippy-tooltip[data-interactive] .tippy-roundarrow path{pointer-events:auto}.tippy-tooltip[data-inertia][data-state=visible]{transition-timing-function:cubic-bezier(.54,1.5,.38,1.11)}.tippy-tooltip[data-inertia][data-state=hidden]{transition-timing-function:ease}.tippy-arrow,.tippy-roundarrow{position:absolute;width:0;height:0}.tippy-roundarrow{width:18px;height:7px;fill:#333;pointer-events:none}.tippy-backdrop{position:absolute;background-color:#333;border-radius:50%;width:calc(110% + 2rem);left:50%;top:50%;z-index:-1;transition:all cubic-bezier(.46,.1,.52,.98);-webkit-backface-visibility:hidden;backface-visibility:hidden}.tippy-backdrop:after{content:"";float:left;padding-top:100%}.tippy-backdrop+.tippy-content{transition-property:opacity;will-change:opacity}.tippy-backdrop+.tippy-content[data-state=hidden]{opacity:0}'), ut });
//# sourceMappingURL=index.all.min.js.map

/*======================================*/




(function () {

  var urlParams = new URLSearchParams(window.location.search);
  var translator = urlParams.get('translator');

  if (!translator && window.user && window.user.email && window.user.email.indexOf('_ganttPROtranslator') !== -1) {
    translator = window.user.email.split('_ganttPROtranslator')[0];
  }

  // Remove trailing slash from translator parameter
  if (translator && translator.endsWith('/')) {
    translator = translator.replace(/\/+$/, '');
  }

  var closeSvg = `
  <svg class="js-translator-tooltip-editor-close-icon" viewPort="0 0 12 12" version="1.1"
  xmlns="http://www.w3.org/2000/svg">
  <line x1="1" y1="11"
        x2="11" y2="1"
        stroke="black"
        stroke-width="2"/>
  <line x1="1" y1="1"
        x2="11" y2="11"
        stroke="black"
        stroke-width="2"/>
  </svg>`;

  var user = false;
  var fallbackLanguage = 'en';

  translationStorage = false;
  var ajaxPath;
  var productId;
  var requestedLocale;

  for (s in document.scripts) {
    var marker = '/translator/translator.js';
    var versionMarker = 'product='
    var localeMarker = 'locale='
    if (document.scripts[s].src && document.scripts[s].src.indexOf(marker) !== -1) {
      ajaxPath = document.scripts[s].src.split(marker)[0];
      if (document.scripts[s].src.indexOf(versionMarker) !== -1) {
        productId = document.scripts[s].src.split(versionMarker)[1].split('&')[0];
      }
    }
  }

  // Check if logging is needed (only on translation domain)
  var shouldLog = window.location.hostname.includes('translation.ganttpro');
  
  // Functions for conditional logging
  var translatorLog = function() {
    if (shouldLog) {
      console.log.apply(console, arguments);
    }
  };
  
  var translatorError = function() {
    if (shouldLog) {
      console.error.apply(console, arguments);
    }
  };

  // Log translator information (may be empty for regular users)
  if (!translator || translator.trim() === '') {
    translatorLog('[TRANSLATOR] No translator parameter provided - working in general mode');
  }

  if (!productId || productId.trim() === '') {
    translatorError('[TRANSLATOR] Missing or invalid productId in script URL');
    return;
  }

  if (!ajaxPath || ajaxPath.trim() === '') {
    translatorError('[TRANSLATOR] Missing or invalid ajaxPath in script URL');
    return;
  }

  translatorLog('[TRANSLATOR] Initialized with productId:', productId, 'ajaxPath:', ajaxPath);

  // // VPN pop-up if access to translation API is blocked by server IP check (no external services)
  // (function() {
  //   try {
  //     var probeUrl = ajaxPath + '/api/ping?ts=' + Date.now();
  //     fetch(probeUrl, { method: 'GET', cache: 'no-store' })
  //       .then(function(resp){
  //         if (resp.status === 403) {
  //           var wrap = document.createElement('div');
  //           wrap.style.position = 'fixed';
  //           wrap.style.zIndex = '2147483647';
  //           wrap.style.left = '0';
  //           wrap.style.right = '0';
  //           wrap.style.top = '0';
  //           wrap.style.padding = '12px 16px';
  //           wrap.style.background = 'rgba(220, 0, 0, 0.9)';
  //           wrap.style.color = '#fff';
  //           wrap.style.fontFamily = 'Inter, Arial, sans-serif';
  //           wrap.style.fontSize = '14px';
  //           wrap.style.textAlign = 'center';
  //           wrap.textContent = 'Translation service works only under internal VPN.';
  //           document.body.appendChild(wrap);
  //           setTimeout(function(){ if (wrap && wrap.parentNode) wrap.parentNode.removeChild(wrap); }, 10000);
  //         }
  //       })
  //       .catch(function(){ /* ignore */ });
  //   } catch (e) {}
  // })();

  window.updateGanttPROUsedTranslationKeys = function (keys) {
    fetch(ajaxPath + '/api/external/updateusedkeys/' + productId, {
      method: 'POST', // or 'PUT'
      body: keys, // data can be `string` or {object}!
      // mode: 'no-cors', // no-cors
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      }
    })
      .then(function (data) {

      })
      .catch(function (e) {
        translatorError('window.updateGanttPROUsedTranslationKeys', e);
      })
  };

  if (!document.querySelector('.js-translator')) return;

  var currntLanguage = document.querySelector('.js-translator').dataset.translationLocale;
  document.body.classList.add('js-translator-document-body');
  
  // Check if translator parameter exists in URL to show overlay
  var shouldShowOverlay = urlParams.has('translator');
  
  // Functions for loading overlay (created only if needed)
  var createLoadingOverlay, updateLoadingStatus, removeLoadingOverlay;
  
  if (shouldShowOverlay) {
    createLoadingOverlay = function() {
      var overlay = document.createElement('div');
      overlay.className = 'js-translator-loading-overlay';
      overlay.innerHTML = `
        <div class="js-translator-loading-content">
          <div class="js-translator-loading-spinner"></div>
          <div id="js-translator-loading-status">Initializing translator...</div>
          <div class="js-translator-loading-locale">Locale: ${currntLanguage}</div>
          <div class="js-translator-loading-info">This may take up to 1 minute</div>
        </div>
      `;
      document.body.appendChild(overlay);
    };

    updateLoadingStatus = function(message) {
      var statusElement = document.getElementById('js-translator-loading-status');
      if (statusElement) {
        statusElement.textContent = message;
      }
    };

    removeLoadingOverlay = function() {
      var overlay = document.querySelector('.js-translator-loading-overlay');
      if (overlay) {
        overlay.remove();
      }
    };
    
    // Show overlay only if translator parameter exists
    createLoadingOverlay();
    updateLoadingStatus('Checking translator parameters...');
  } else {
    // Empty functions if overlay is not needed
    createLoadingOverlay = function() {};
    updateLoadingStatus = function() {};
    removeLoadingOverlay = function() {};
  }
  
  // Логируем исходный translator для отладки
  if (translator) {
    translatorLog('[TRANSLATOR CLIENT] Original translator parameter:', JSON.stringify(translator));
  }

  var submit = function (url, data) {

    return new Promise(function (resolve, reject) {
      fetch(ajaxPath + '/api/external' + url + translator + '/' + productId, {
        method: 'POST', // или 'PUT'
        body: JSON.stringify(data), // data может быть типа `string` или {object}!
        //mode: 'no-cors', // no-cors
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        }
      })
        .then(
          function (response) {
            if (response.status !== 200) {
              translatorError(response);
              reject(response);
              return;
            }
            // Examine the text in the response
            response.json().then(function (data) {
              resolve(data);
            });
          }
        )
        .catch(function (err) {
          translatorError('Fetch Error :-S', err);
          reject(err)
        });
    });
  };

  var removeTags = function (input) {
    var regex = /(<([^>]+)>)/ig
    return input.replace(regex, "");
  }

  var patchLinks = function () {
    var links = document.querySelectorAll('a[href]');
    for (var l in links) {
      if (links[l].getAttribute && links[l].getAttribute('href').indexOf('http') !== 0 && links[l].getAttribute('href').indexOf('#') === -1) {
        links[l].setAttribute('href', links[l].getAttribute('href') + '?translator=' + translator);
      }
    }
  }

  var buildUiForHiddenText = function () {
    var hiddenTextsUiContainer = document.createElement('div');
    hiddenTextsUiContainer.classList.add('js-translator-hidden-texts-ui-container');
    document.body.appendChild(hiddenTextsUiContainer);
    var toTranslate = [];
    var title = document.querySelector("title");
    var metaTitle = document.querySelector("meta[itemprop='name']");
    var metaDescription = document.querySelector("meta[itemprop='description']");
    var imageAlts = document.querySelectorAll("img[alt^='<span']"); // only alts with translations
    var svgTexts = document.querySelectorAll("tspan"); // only alts with translations
    if (title) {
      toTranslate.push({ html: title.innerText, description: 'Page title' });
      title.innerText = removeTags(title.innerText);
    }
    if (metaTitle) toTranslate.push({ html: metaTitle.getAttribute('content'), description: 'Meta title' });
    if (metaDescription) toTranslate.push({ html: metaDescription.getAttribute('content'), description: 'Meta description' });
    if (imageAlts) {
      imageAlts.forEach(function (val) {
        toTranslate.push({ html: val.getAttribute('alt'), description: `<img src="${val.getAttribute('src') || val.getAttribute('data-src')}">` });
      })
    }
    if (svgTexts) {
      svgTexts.forEach(function (val, index) {
        var html = unescape(val.textContent);
        var d = document.createElement('div');
        d.innerHTML = html;
        var text = d.textContent;
        toTranslate.push({ html: html, description: `svg text label` });
        val.innerHTML = text;
      })
    }
    var html = '<table>';
    toTranslate.forEach(function (val) {
      html += `
      <tr>
        <td>
          ${val.description}
        </td>
        <td>
          ${val.html}
        </td>
      </tr>
      `
    });
    html += '</table>';
    hiddenTextsUiContainer.innerHTML = html;
  };

  var initAdminHandlers = function (node) {
    var translatorNodes = document.querySelectorAll('.js-translator');

    for (trNode in translatorNodes) {
      var currentTrNode = translatorNodes[trNode];
      if (!currentTrNode._tippy) {
        // Draft system removed - only contextmenu editing needed

        tippy(currentTrNode, {
          interactive: true,
          trigger: 'contextmenu',
          theme: 'light',
          size: 'large',
          hideOnClick: false,
          boundary: 'viewport',
          arrow: true,
          maxWidth: 900,
          multiple: true,
          onTrigger: function (instance, e) {
            e.stopPropagation();
            e.preventDefault();
          },
          onShow: function (instance) {
            var prefixesString = '';

            var nodeTranslationData = getNodeTranslationData(instance.reference);

            nodeTranslationData.keys.split(',').forEach(function (k) {
              if (k == nodeTranslationData.key) {
                prefixesString += `<strong>${k}</strong><br>`
              } else {
                prefixesString += `<span>${k}</span><br>`
              }
            });

            instance.setContent(`
              <div class="js-translator-tooltip-editor">
                <div class="js-translator-tooltip-editor-header">
                  ${prefixesString}
                </div>
                <div class="js-translator-tooltip-editor-inputs-container">
                  <div ${(!nodeTranslationData.fallback.value && currntLanguage === fallbackLanguage) ? 'style="display:none"' : ''} class="js-translator-tooltip-editor-text">
                    <label><strong>English</strong> (Original)</label>
                    <div class="js-translator-tooltip-editor-text-orig">${nodeTranslationData.fallback.value || '[There is no English translation]'}</div>
                  </div>
                  <div class="js-translator-tooltip-editor-inputs">
                    <label><strong>${currntLanguage.toUpperCase()}</strong></label>
                    <textarea class="js-translator-tooltip-editor-active">${nodeTranslationData.current.value || ''}</textarea>
                  </div>
                </div>
                <div class="js-translator-tooltip-editor-footer">
                  <a class="js-translator-tooltip-editor-button">Save<div class="spinner-border text-success" role="status"><span class="sr-only"></span></div></a>
                </div>${closeSvg}
              </div>
            `);

            var editorOriginal = instance.popper.querySelector('.js-translator-tooltip-editor-text-orig');
            var editor = instance.popper.querySelector('.js-translator-tooltip-editor-active');
            var saveButton = instance.popper.querySelector('.js-translator-tooltip-editor-button');
            var closeButton = instance.popper.querySelector('.js-translator-tooltip-editor-close-icon');
            var container = instance.popper.querySelector('.js-translator-tooltip-editor');


            container.onclick = function (e) {
              e.stopPropagation();
            }

            setTimeout(function () {
              editor.focus();
              addInEditClass();
            }, 100)

            var addInEditClass = function () {
              if (instance.reference && instance.reference.classList) {
                instance.reference.classList.add('js-translator-hide-highlights');
              }
            }
            var removeInEditClass = function () {
              if (instance.reference && instance.reference.classList) {
                instance.reference.classList.remove('js-translator-hide-highlights');
              }
            }

            saveButton.onclick = function (e) {
              e.stopPropagation();
              
              // Проверяем что у нас есть валидные данные для сохранения
              if (!nodeTranslationData.key) {
                translatorError('[TRANSLATOR CLIENT] Cannot save: missing translation key');
                saveButton.classList.remove('js-translator-tooltip-editor-button-loading');
                return;
              }
              
              if (translationStorage.translations[currntLanguage][nodeTranslationData.key] && editor.value === translationStorage.translations[currntLanguage][nodeTranslationData.key].value) {
                return instance.hide();
              }
              saveButton.classList.add('js-translator-tooltip-editor-button-loading');
              var toSaveObj = {
                value: editor.value, // Сразу сохраняем как финальное значение
                locale: currntLanguage,
                key: nodeTranslationData.key,
                productId: productId
              };

              translatorLog('[TRANSLATOR CLIENT] Saving translation:', toSaveObj);

              fetch(ajaxPath + '/api/external/translation/' + translator + '/' + productId, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify(toSaveObj),
              })
                .then(response => {
                  if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                  }
                  return response.json();
                })
                .then(data => {
                  // Теперь API возвращает конкретный перевод в data.translation
                  if (data.translation) {
                    translationStorage.translations[currntLanguage][nodeTranslationData.key] = data.translation;
                  } else {
                    // Fallback: создаем объект перевода локально
                    translationStorage.translations[currntLanguage][nodeTranslationData.key] = {
                      value: editor.value,
                      key: nodeTranslationData.key,
                      locale: currntLanguage
                    };
                  }
                  
                  highlightOne(instance.reference);
                  instance.hide();
                  removeInEditClass();
                  instance.reference.innerHTML = editor.value;
                  
                  saveButton.classList.remove('js-translator-tooltip-editor-button-loading');
                })
                .catch((error) => {
                  saveButton.classList.remove('js-translator-tooltip-editor-button-loading');
                  translatorError('[TRANSLATOR CLIENT] Save error:', error);
                });
            }
            closeButton.onclick = function (e) {
              e.stopPropagation();
              instance.hide();
              removeInEditClass();
            } 
            editor.onkeyup = function () {

              //
            }
          }
        });
      }
    }

  }

  var getNodeTranslationData = function (currentTrNode) {
    if (!currentTrNode || !currentTrNode.dataset) {
      translatorError('[TRANSLATOR CLIENT] Invalid node passed to getNodeTranslationData:', currentTrNode);
      return {
        key: '',
        keys: '',
        fallback: {},
        current: {}
      };
    }
    
    var out = {};
    out.key = currentTrNode.dataset.translationKey;
    out.keys = currentTrNode.dataset.translationKeys;
    out.fallback = translationStorage.translations[fallbackLanguage][out.key] || {};
    out.current = translationStorage.translations[currntLanguage][out.key] || {};
    return out;
  }

  function countWords(str) {
    if (!str) return 0;
    var matches = str.match(/[\w\d\’\'-]+/gi);
    return matches ? matches.length : 0;
  }

  var calculateOnPageStats = function () {
    var translatorNodes = document.querySelectorAll('.js-translator');
    var stats = { translatedCount: 0, notTranslatedCount: 0, approvedTranslatedCount: 0 };
    var keysCalculated = [];
    for (trNode in translatorNodes) {
      var currentTrNode = translatorNodes[trNode];

      if (!currentTrNode || !currentTrNode.dataset) break;

      var nodeTranslationData = getNodeTranslationData(currentTrNode);


      if (1
        && nodeTranslationData.current.value * 1 != nodeTranslationData.current.value
        && nodeTranslationData.fallback.value * 1 != nodeTranslationData.fallback.value
        && nodeTranslationData.fallback.value
        && keysCalculated.indexOf(nodeTranslationData.key) === -1) {
        if (!nodeTranslationData.current.value) {
          keysCalculated.push(nodeTranslationData.key);
          stats.notTranslatedCount += countWords(nodeTranslationData.fallback.value);
        } else if (nodeTranslationData.current.value) {
          keysCalculated.push(nodeTranslationData.key);
          stats.translatedCount += countWords(nodeTranslationData.fallback.value);
          // All translations are now approved immediately
          stats.approvedTranslatedCount += countWords(nodeTranslationData.fallback.value);
        }
      } else {
        //console.log(' 2 Keys with not counted words', nodeTranslationData.key, nodeTranslationData.fallback.value)
      }
    }
    return stats;
  }

  var highlight = function () {
    var translatorNodes = document.querySelectorAll('.js-translator');
    for (let trNode in translatorNodes) {
      var currentTrNode = translatorNodes[trNode];
      if (currentTrNode && currentTrNode.dataset) {
        highlightOne(currentTrNode);
      };
    }

    var translatorNodesPlaceholders = document.querySelectorAll("input[placeholder^='<span'], textarea[placeholder^='<span']");
    for (let trNode in translatorNodesPlaceholders) {
      var currentTrNode = translatorNodesPlaceholders[trNode];
      if (currentTrNode && currentTrNode.getAttribute) {
        var currentPlaceholder = currentTrNode.getAttribute('placeholder');
        currentTrNode.dataset.translationKey = currentPlaceholder.split('data-translation-key=')[1].split(' ')[0].split('>')[0];
        currentTrNode.dataset.translationKeys = currentPlaceholder.split('data-translation-keys=')[1].split(' ')[0].split('>')[0];
        highlightOne(currentTrNode);
      }
    }

    var translatorNodesButtons = document.querySelectorAll("button");
    for (let trNode in translatorNodesButtons) {
      var currentTrNode = translatorNodesButtons[trNode];
      if (currentTrNode && currentTrNode.textContent && currentTrNode.textContent.length && currentTrNode.textContent.indexOf('<span') === 0) {
        var currentValue = currentTrNode.textContent;
        currentTrNode.dataset.translationKey = currentValue.split('data-translation-key=')[1].split(' ')[0].split('>')[0];
        currentTrNode.dataset.translationKeys = currentValue.split('data-translation-keys=')[1].split(' ')[0].split('>')[0];
        highlightOne(currentTrNode);
      }
    }
  }

  var setPlaceholderIfInput = function (node, placeholder) {
    if (node.nodeName.toLowerCase() === 'input' || node.nodeName.toLowerCase() === 'textarea') {
      node.setAttribute('placeholder', placeholder);
      //node.value = '';
    }
  }


  var setInnerTextIfButton = function (node, text) {
    if (node.nodeName.toLowerCase() === 'button') {
      node.innerText = text;
    }
  }


  var highlightOne = function (currentTrNode) {
    if (!currentTrNode || !currentTrNode.classList) {
      translatorError('[TRANSLATOR CLIENT] Invalid node passed to highlightOne:', currentTrNode);
      return;
    }
    
    var value;
    var nodeTranslationData = getNodeTranslationData(currentTrNode);
    currentTrNode.classList.remove('js-translator-lang-translated');
    currentTrNode.classList.remove('js-translator-fallback-translated');
    // Draft classes removed - no longer needed
    currentTrNode.classList.remove('js-translator-never-translated');
    currentTrNode.classList.add('js-translator');
    
    if (!!nodeTranslationData.current.value) {
      value = translationStorage.translations[currntLanguage][nodeTranslationData.key].value;
      currentTrNode.classList.add('js-translator-lang-translated');
    } else if (!!nodeTranslationData.fallback.value) {
      value = translationStorage.translations[fallbackLanguage][nodeTranslationData.key].value;
      currentTrNode.classList.add('js-translator-fallback-translated');
    } else {
      value = nodeTranslationData.key;
      currentTrNode.classList.add('js-translator-never-translated');
    }
    setPlaceholderIfInput(currentTrNode, value);
    setInnerTextIfButton(currentTrNode, value);
    
    // Применяем перевод к обычным текстовым элементам (div, span, h1, p и т.д.)
    var nodeName = currentTrNode.nodeName.toLowerCase();
    if (nodeName !== 'input' && nodeName !== 'textarea' && nodeName !== 'button') {
      if (currentTrNode.innerHTML !== value) {
        currentTrNode.innerHTML = value;
      }
    }
  };

  function findByText(rootElement, text) {
    var filter = {
      acceptNode: function (node) {
        // look for nodes that are text_nodes and include the following string.
        if (node.nodeType === document.TEXT_NODE && node.nodeValue.includes(text)) {
          return NodeFilter.FILTER_ACCEPT;
        }
        return NodeFilter.FILTER_REJECT;
      }
    }
    var nodes = [];
    var walker = document.createTreeWalker(rootElement, NodeFilter.SHOW_TEXT, filter, false);
    while (walker.nextNode()) {
      //give me the element containing the node
      nodes.push(walker.currentNode.parentNode);
    }
    return nodes;
  }



  var convertVueText = function () {
    var nodes = findByText(document.body, 'js-translator');
    for (var i = 0; i < nodes.length; i++) {
      //do something with nodes[i]
      nodes[i].innerHTML = nodes[i].innerText;
    }
  }

  var addPointerEvents = function () {
    var translatorNodes = document.querySelectorAll('.js-translator');
    for (trNode in translatorNodes) {
      var currentTrNode = translatorNodes[trNode];
      if (currentTrNode && currentTrNode.style) {
        currentTrNode.style.pointerEvents = 'all';
      };
    }
  }

  // Статистический бар убран - не нужен



  var initTranslatorUi = function (storage) {
    translatorLog('[TRANSLATOR CLIENT] Initializing translator UI. Current language:', currntLanguage, 'Available locales:', Object.keys(storage.translations || {}));

    translationStorage = storage;
    if (!translationStorage.translations[currntLanguage]) {
      translationStorage.translations[currntLanguage] = {};
    }
    user = translationStorage.user;

    if (user.locale && currntLanguage !== user.locale) {
      translatorError('[TRANSLATOR CLIENT] Locale mismatch: user allowed:', user.localeName, 'trying to translate:', currntLanguage);
      return false;
    }

    addPointerEvents();
    highlight();
    patchLinks();
    initAdminHandlers();

    translatorLog('[TRANSLATOR CLIENT] Translator UI initialized successfully');

  }

  // Используем requestedLocale из URL скрипта, если передана, иначе currntLanguage из DOM
  var localeToRequest = requestedLocale || currntLanguage;
  
  translatorLog('[TRANSLATOR CLIENT] Starting locale loading for translator:', translator, 'productId:', productId, 'locale:', localeToRequest);
  
  updateLoadingStatus('Connecting to translation server...');
  
  var apiUrl = translator 
    ? ajaxPath + '/api/external/user/' + translator + '/' + productId + (localeToRequest ? '?locale=' + localeToRequest : '')
    : ajaxPath + '/api/external/user/guest/' + productId + (localeToRequest ? '?locale=' + localeToRequest : '');
    
  fetch(apiUrl).then(
    function (response) {
      if (response.status !== 200) {
        translatorError('[TRANSLATOR CLIENT] Failed to load translation data. Status:', response.status);
        updateLoadingStatus('Error: Failed to load translation data');
        setTimeout(function() {
          removeLoadingOverlay();
        }, 3000);
        return;
      }
      // Examine the text in the response
      response.json().then(function (data) {
        translatorLog('[TRANSLATOR CLIENT] Locale data received. User:', data.user?.login || data.user?.username || data.user?.id, 'Locales:', Object.keys(data.translations || {}));
        
        updateLoadingStatus('Processing translation data...');
        
        buildUiForHiddenText(data);
        
        updateLoadingStatus('Initializing translator interface...');
        
        initTranslatorUi(data);
        
        // Убираем оверлей загрузки с небольшой задержкой для плавности
        setTimeout(function() {
          removeLoadingOverlay();
        }, 500);
        
        setInterval(function () {
          convertVueText();
          initAdminHandlers();
          highlight();
          addPointerEvents();
        }, 1000)

      });
    }
  )
    .catch(function (err) {
      translatorError('[TRANSLATOR CLIENT] Error loading locale data:', err);
      updateLoadingStatus('Error loading translation data');
      setTimeout(function() {
        removeLoadingOverlay();
      }, 2000);
    });

})();






