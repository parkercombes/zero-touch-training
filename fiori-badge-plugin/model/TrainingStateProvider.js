/**
 * TrainingStateProvider.js
 * Zero-Touch Training — Fiori Badge Plugin
 *
 * Abstracts training state retrieval. Priority:
 *   1. In-memory cache (populated on first load)
 *   2. REST API (trainingApiUrl from manifest config, if set)
 *   3. localStorage (PoC fallback — always available)
 *
 * State shape per app ID:
 * {
 *   appId:        string,   // matches Fiori semantic object / tile ID
 *   title:        string,   // display name for popover header
 *   scenario:     string,   // scenario key passed to training portal
 *   status:       "assigned" | "progress" | "done",
 *   currentLevel: 1 | 2 | 3 | 4,
 *   completedAt:  ISO string | null
 * }
 *
 * localStorage key: "ztt_training_state"
 * Value: JSON object keyed by appId
 *
 * Seed data (PoC):  call TrainingStateProvider.seed() from browser console
 * or load via REST by setting trainingApiUrl in manifest config.
 */
sap.ui.define([], function () {
    "use strict";

    /* ------------------------------------------------------------------ */
    /*  Default seed data — five goods-receipt scenarios from the PoC      */
    /* ------------------------------------------------------------------ */
    var DEFAULT_SEED = {
        "goods-receipt-standard": {
            appId: "goods-receipt-standard",
            title: "Goods Receipt (Standard PO)",
            scenario: "goods-receipt-standard",
            status: "progress",
            currentLevel: 2
        },
        "goods-receipt-blind": {
            appId: "goods-receipt-blind",
            title: "Goods Receipt (Blind)",
            scenario: "goods-receipt-blind",
            status: "assigned",
            currentLevel: 1
        },
        "goods-receipt-partial": {
            appId: "goods-receipt-partial",
            title: "Goods Receipt (Partial)",
            scenario: "goods-receipt-partial",
            status: "assigned",
            currentLevel: 1
        },
        "goods-receipt-return": {
            appId: "goods-receipt-return",
            title: "Return Delivery",
            scenario: "goods-receipt-return",
            status: "done",
            currentLevel: 4,
            completedAt: new Date(Date.now() - 86400000 * 3).toISOString()
        },
        "goods-receipt-split-valuation": {
            appId: "goods-receipt-split-valuation",
            title: "Goods Receipt (Split Valuation)",
            scenario: "goods-receipt-split-valuation",
            status: "assigned",
            currentLevel: 1
        },
        /* Generic tile ID aliases — used when exact scenario ID is unknown */
        "create-purchase-order": {
            appId: "create-purchase-order",
            title: "Create Purchase Order",
            scenario: "goods-receipt-standard",
            status: "progress",
            currentLevel: 2
        },
        "manage-purchase-orders": {
            appId: "manage-purchase-orders",
            title: "Manage Purchase Orders",
            scenario: "goods-receipt-standard",
            status: "assigned",
            currentLevel: 1
        }
    };

    var STORAGE_KEY = "ztt_training_state";
    var _cache = null;        // populated on first call to _ensureLoaded()
    var _apiUrl = null;       // set from manifest config by Component.js
    var _portalUrl = "/training/";

    /* ------------------------------------------------------------------ */
    /*  Internal helpers                                                    */
    /* ------------------------------------------------------------------ */

    function _readLocalStorage() {
        try {
            var raw = window.localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function _writeLocalStorage(state) {
        try {
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) { /* quota exceeded or private mode — ignore */ }
    }

    function _ensureLoaded() {
        if (_cache) return;
        var stored = _readLocalStorage();
        _cache = stored || Object.assign({}, DEFAULT_SEED);
        if (!stored) {
            _writeLocalStorage(_cache); // persist seed for next load
        }
    }

    /* ------------------------------------------------------------------ */
    /*  Public API                                                          */
    /* ------------------------------------------------------------------ */

    var TrainingStateProvider = {

        /**
         * Called by Component.js during init to wire manifest config.
         * @param {object} config  { trainingApiUrl, trainingPortalUrl }
         */
        configure: function (config) {
            _apiUrl = (config && config.trainingApiUrl) || null;
            _portalUrl = (config && config.trainingPortalUrl) || "/training/";
        },

        /**
         * Retrieve training state for a single app/tile ID.
         * Returns null if no training is configured for that tile.
         *
         * @param  {string} appId
         * @returns {object|null}
         */
        getState: function (appId) {
            _ensureLoaded();
            return _cache[appId] || null;
        },

        /**
         * Return a map of all known states. Used by Component.js
         * to build a reverse lookup from DOM tile IDs.
         * @returns {object}
         */
        getAllStates: function () {
            _ensureLoaded();
            return _cache;
        },

        /**
         * Update a learner's level after completing a training step.
         * Advances status: assigned → progress → done.
         *
         * @param {string} appId
         * @param {number} completedLevel  1-4
         */
        recordProgress: function (appId, completedLevel) {
            _ensureLoaded();
            if (!_cache[appId]) return;

            var entry = _cache[appId];
            var nextLevel = completedLevel + 1;

            if (nextLevel > 4) {
                entry.status = "done";
                entry.currentLevel = 4;
                entry.completedAt = new Date().toISOString();
            } else {
                entry.status = "progress";
                entry.currentLevel = nextLevel;
            }

            _writeLocalStorage(_cache);
        },

        /**
         * Build the URL to launch the training portal for a tile.
         * @param {string} appId
         * @param {string} mode  "practice" | "help"
         * @returns {string}
         */
        getLaunchUrl: function (appId, mode) {
            _ensureLoaded();
            var entry = _cache[appId];
            var scenario = (entry && entry.scenario) || appId;
            return _portalUrl + "?scenario=" + encodeURIComponent(scenario) +
                   "&mode=" + encodeURIComponent(mode || "practice");
        },

        /**
         * Seed or reset state (dev / testing use only).
         * Call from browser console: TrainingStateProvider.seed()
         */
        seed: function (overrides) {
            _cache = Object.assign({}, DEFAULT_SEED, overrides || {});
            _writeLocalStorage(_cache);
            return _cache;
        },

        /**
         * Clear all state (dev use only).
         */
        clear: function () {
            _cache = null;
            try { window.localStorage.removeItem(STORAGE_KEY); } catch (e) {}
        }
    };

    return TrainingStateProvider;
});
