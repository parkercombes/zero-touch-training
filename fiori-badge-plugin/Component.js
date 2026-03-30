/**
 * Component.js
 * Zero-Touch Training — Fiori Badge Plugin
 *
 * SAP BTP Fiori Launchpad Shell Plugin.
 *
 * Lifecycle:
 *   1. BTP Launchpad loads this plugin during shell bootstrap.
 *   2. init() fires; we attach to the renderer-created event.
 *   3. Once the shell is rendered, a MutationObserver watches for tiles.
 *   4. Each tile gets a training badge injected into its DOM (top-right corner).
 *   5. Tapping a badge opens the four-level progression popover.
 *   6. Popover links launch the training portal with ?scenario=&mode= params.
 *
 * Badge states (driven by TrainingStateProvider):
 *   assigned  — gray  + ▶ play icon   (training available, not started)
 *   progress  — amber + level number  (in-progress)
 *   done      — green + ✓ checkmark   (all four levels complete)
 *
 * DDR references:
 *   DDR-001: Badge style → solid number badge (Style A)
 *   DDR-002: Tap target  → 48px invisible ::after hit area on 26px visual
 *   DDR-006: Context mode → badge tap defaults to "practice"
 *
 * Deployment notes (BTP):
 *   - Upload fiori-badge-plugin/ folder to an HTML5 repository in BTP.
 *   - In BTP Launchpad Service → Content Manager → Apps → Create App,
 *     set type = "Shell Plugin", point to this component.
 *   - Assign to a role; users with that role get badges at next login.
 */
sap.ui.define([
    "sap/ui/core/Component",
    "com/zerotouchtraining/badgeplugin/model/TrainingStateProvider"
], function (Component, TrainingStateProvider) {
    "use strict";

    /* ------------------------------------------------------------------ */
    /*  Level metadata — drives popover track                               */
    /* ------------------------------------------------------------------ */
    var LEVELS = [
        { id: 1, name: "EXPLORE",      sub: "Observe the process" },
        { id: 2, name: "GUIDED",       sub: "Follow along with prompts" },
        { id: 3, name: "ON YOUR OWN",  sub: "Complete without guidance" },
        { id: 4, name: "CHALLENGE",    sub: "Speed run for mastery" }
    ];

    /* Tile selectors — BTP Fiori renders tiles in several component variants */
    var TILE_SELECTORS = [
        ".sapUshellTile:not([data-ztt])",
        ".sapMGT:not([data-ztt])",       /* Generic Tile (most BTP tiles) */
        ".sapFCard:not([data-ztt])"      /* Card tile (Spaces/Pages model) */
    ];

    /* ------------------------------------------------------------------ */
    /*  Component definition                                                */
    /* ------------------------------------------------------------------ */
    return Component.extend("com.zerotouchtraining.badgeplugin.Component", {

        metadata: { manifest: "json" },

        /* ---- Lifecycle ------------------------------------------------ */

        init: function () {
            Component.prototype.init.apply(this, arguments);

            // Wire TrainingStateProvider with manifest config
            var config = this.getManifestEntry("/sap.ui5/config") || {};
            TrainingStateProvider.configure(config);

            // Load CSS once
            this._injectStylesheet();

            // Attach after shell renderer is ready (tiles don't exist yet)
            if (sap.ushell && sap.ushell.Container) {
                sap.ushell.Container.attachRendererCreatedEvent(
                    this._onRendererCreated.bind(this)
                );
            } else {
                // Fallback: wait for DOMContentLoaded (standalone / test harness)
                if (document.readyState === "loading") {
                    document.addEventListener("DOMContentLoaded",
                        this._startObserver.bind(this));
                } else {
                    this._startObserver();
                }
            }
        },

        /* ---- Shell event ---------------------------------------------- */

        _onRendererCreated: function () {
            // Give the tile grid a moment to paint before first scan
            setTimeout(this._startObserver.bind(this), 800);
        },

        /* ---- MutationObserver ----------------------------------------- */

        _startObserver: function () {
            // Initial scan of whatever is already on screen
            this._scanAndBadge(document.body);

            // Watch for dynamically added tiles (navigation, group expand, etc.)
            this._observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    mutation.addedNodes.forEach(function (node) {
                        if (node.nodeType === 1 /* ELEMENT_NODE */) {
                            this._scanAndBadge(node);
                        }
                    }, this);
                }, this);
            }.bind(this));

            this._observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        },

        /* ---- Tile scanning -------------------------------------------- */

        _scanAndBadge: function (root) {
            var self = this;
            TILE_SELECTORS.forEach(function (sel) {
                try {
                    var nodes = root.matches && root.matches(sel)
                        ? [root]
                        : Array.from(root.querySelectorAll(sel));

                    nodes.forEach(function (tile) {
                        var appId = self._resolveAppId(tile);
                        if (!appId) return;

                        var state = TrainingStateProvider.getState(appId);
                        if (!state) return; // Tile has no training configured

                        tile.setAttribute("data-ztt", appId); // mark as processed
                        self._injectBadge(tile, appId, state);
                    });
                } catch (e) { /* selector not supported in this browser — skip */ }
            });
        },

        /* ---- App ID resolution ---------------------------------------- */

        /**
         * Walk multiple strategies to extract a meaningful ID from a tile element.
         * BTP tiles expose their target in different ways depending on tile type.
         */
        _resolveAppId: function (tileEl) {
            // Strategy 1: data-ztt-id override (manual mapping for testing)
            var override = tileEl.getAttribute("data-ztt-id");
            if (override) return override;

            // Strategy 2: SAP help-id attribute (set by some tile renderers)
            var helpId = tileEl.getAttribute("data-help-id");
            if (helpId) return helpId;

            // Strategy 3: aria-label → normalize to kebab-case for lookup
            var label = tileEl.getAttribute("aria-label");
            if (label) {
                var normalized = label.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
                if (TrainingStateProvider.getState(normalized)) return normalized;
            }

            // Strategy 4: UI5 element binding context (Generic Tile has title binding)
            var ui5Id = tileEl.id;
            if (ui5Id && sap && sap.ui && sap.ui.getCore) {
                try {
                    var el = sap.ui.getCore().byId(ui5Id);
                    if (el) {
                        // Generic Tile exposes getHeader()
                        if (el.getHeader) {
                            var header = el.getHeader();
                            if (header) {
                                var fromHeader = header.toLowerCase()
                                    .replace(/\s+/g, "-")
                                    .replace(/[^a-z0-9-]/g, "");
                                if (TrainingStateProvider.getState(fromHeader)) return fromHeader;
                            }
                        }
                        // Try binding context path for tile catalog entries
                        var ctx = el.getBindingContext ? el.getBindingContext() : null;
                        if (ctx) {
                            return ctx.getProperty("id") ||
                                   ctx.getProperty("appId") ||
                                   ctx.getProperty("semanticObject") || null;
                        }
                    }
                } catch (e) { /* UI5 not available or element not found */ }
            }

            return null;
        },

        /* ---- Badge injection ------------------------------------------ */

        _injectBadge: function (tileEl, appId, state) {
            // Ensure the tile has a positioning context
            var pos = window.getComputedStyle(tileEl).position;
            if (pos === "static") tileEl.style.position = "relative";

            var badge = document.createElement("div");
            badge.className = "ztt-badge ztt-badge--" + state.status;
            badge.setAttribute("role", "button");
            badge.setAttribute("tabindex", "0");
            badge.setAttribute("aria-label",
                "Training: " + (state.title || appId) +
                (state.status === "progress" ? " — Level " + state.currentLevel : "")
            );

            // Inner content
            if (state.status === "done") {
                badge.innerHTML = '<span class="ztt-badge__icon" aria-hidden="true">✓</span>';
            } else if (state.status === "progress") {
                badge.innerHTML = '<span class="ztt-badge__level" aria-hidden="true">' +
                    state.currentLevel + '</span>';
            } else {
                // assigned
                badge.innerHTML = '<span class="ztt-badge__icon" aria-hidden="true">▶</span>';
            }

            // Interaction — badge tap → popover (Practice mode per DDR-006)
            var self = this;
            badge.addEventListener("click", function (e) {
                e.stopPropagation();
                self._togglePopover(badge, appId, state);
            });
            badge.addEventListener("keydown", function (e) {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    self._togglePopover(badge, appId, state);
                }
            });

            tileEl.appendChild(badge);
        },

        /* ---- Popover -------------------------------------------------- */

        _togglePopover: function (anchorEl, appId, state) {
            var existing = document.getElementById("ztt-popover");
            if (existing) {
                var wasThisTile = existing.dataset.appId === appId;
                existing.remove();
                document.removeEventListener("click", this._popoverDismissHandler);
                if (wasThisTile) return; // second tap on same tile = close
            }
            this._renderPopover(anchorEl, appId, state);
        },

        _renderPopover: function (anchorEl, appId, state) {
            var self = this;

            var pop = document.createElement("div");
            pop.id = "ztt-popover";
            pop.className = "ztt-popover";
            pop.dataset.appId = appId;
            pop.setAttribute("role", "dialog");
            pop.setAttribute("aria-label", "Training progress: " + (state.title || appId));

            /* Header */
            var header = '<div class="ztt-pop__header">' +
                '<span class="ztt-pop__title">' + _esc(state.title || appId) + '</span>' +
                '<button class="ztt-pop__close" aria-label="Close popover">\u00d7</button>' +
                '</div>';

            /* Level progress track */
            var trackItems = LEVELS.map(function (lvl, idx) {
                var cls = "ztt-track__step";
                if (lvl.id < state.currentLevel || state.status === "done") {
                    cls += " ztt-track__step--done";
                } else if (lvl.id === state.currentLevel && state.status !== "done") {
                    cls += " ztt-track__step--active";
                } else {
                    cls += " ztt-track__step--locked";
                }

                var nodeContent = (lvl.id < state.currentLevel || state.status === "done")
                    ? "✓"
                    : String(lvl.id);

                var connector = idx < LEVELS.length - 1
                    ? '<div class="ztt-track__connector"></div>'
                    : "";

                return '<div class="' + cls + '">' +
                    '<div class="ztt-track__node" aria-hidden="true">' + nodeContent + '</div>' +
                    '<div class="ztt-track__label">' +
                        '<span class="ztt-track__name">' + lvl.name + '</span>' +
                        '<span class="ztt-track__sub">' + lvl.sub + '</span>' +
                    '</div>' +
                '</div>' + connector;
            }).join("");

            var track = '<div class="ztt-pop__track">' + trackItems + '</div>';

            /* Action buttons */
            var practiceUrl = TrainingStateProvider.getLaunchUrl(appId, "practice");
            var helpUrl     = TrainingStateProvider.getLaunchUrl(appId, "help");

            var actions = '<div class="ztt-pop__actions">' +
                '<a href="' + practiceUrl + '" class="ztt-pop__btn ztt-pop__btn--primary">Practice</a>' +
                '<a href="' + helpUrl     + '" class="ztt-pop__btn ztt-pop__btn--secondary">Help Now</a>' +
                '</div>';

            pop.innerHTML = header + track + actions;

            /* Close button */
            pop.querySelector(".ztt-pop__close").addEventListener("click", function () {
                pop.remove();
                document.removeEventListener("click", self._popoverDismissHandler);
            });

            document.body.appendChild(pop);
            this._positionPopover(pop, anchorEl);

            /* Focus for accessibility */
            pop.querySelector(".ztt-pop__close").focus();

            /* Click-outside dismiss */
            this._popoverDismissHandler = function (e) {
                if (!pop.contains(e.target) && e.target !== anchorEl) {
                    pop.remove();
                    document.removeEventListener("click", self._popoverDismissHandler);
                }
            };
            setTimeout(function () {
                document.addEventListener("click", self._popoverDismissHandler);
            }, 0);
        },

        _positionPopover: function (pop, anchor) {
            var rect = anchor.getBoundingClientRect();
            var popW = 260;

            var top  = rect.bottom + window.scrollY + 8;
            var left = rect.left + window.scrollX;

            // Keep within viewport
            if (left + popW > window.innerWidth - 16) {
                left = window.innerWidth - popW - 16;
            }
            if (left < 8) left = 8;

            pop.style.top  = top  + "px";
            pop.style.left = left + "px";
        },

        /* ---- CSS injection -------------------------------------------- */

        _injectStylesheet: function () {
            if (document.getElementById("ztt-badge-css")) return;
            var link = document.createElement("link");
            link.id   = "ztt-badge-css";
            link.rel  = "stylesheet";
            link.href = sap.ui.require.toUrl
                ? sap.ui.require.toUrl("com/zerotouchtraining/badgeplugin/css/ZeroTouchBadges.css")
                : "css/ZeroTouchBadges.css";
            document.head.appendChild(link);
        },

        /* ---- Cleanup -------------------------------------------------- */

        exit: function () {
            if (this._observer) this._observer.disconnect();
            var pop = document.getElementById("ztt-popover");
            if (pop) pop.remove();
            document.removeEventListener("click", this._popoverDismissHandler);
        }
    });

    /* ------------------------------------------------------------------ */
    /*  Utility                                                             */
    /* ------------------------------------------------------------------ */
    function _esc(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }
});
