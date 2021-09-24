class UID2 {
    constructor() {
        this.base_url = "{{ base_url }}";
        this.handleResponse = (resp) => {
            this.setIdentity(JSON.parse(resp)["body"]);
        };
        
        this.getIdentity = () => {
            const payload = this.getCookie("__uid_2");
            if (payload) {
               return JSON.parse(payload);
            }
        };
        this.getAdvertisingToken = () => {
            const identity = this.getIdentity();
            if (identity) {
                return identity["advertising_token"];
            }
        };
        this.setIdentity = (value) => {
            var payload;
            if (typeof (value) === "object") {
                payload = JSON.stringify(value);
            }
            else {
                payload = value;
            }
            this.setCookie("__uid_2", payload);
        };
        this.setCookie = (name, value) => {
            var days = 7;
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = name + "=" + encodeURIComponent(value) + " ;path=/;expires=" + date.toUTCString();
        };
        this.getCookie = (name) => {
            const docCookie = document.cookie;
            if (docCookie) {
                var payload = docCookie.split('; ').find(row => row.startsWith(name));
                if (payload) {
                    return decodeURIComponent(payload.split('=')[1]);
                }
            }
            else {
                return undefined;
            }
        };
        this.removeCookie = (name) => {
            document.cookie = name + "=;path=/;expires=Tue, 1 Jan 1980 23:59:59 GMT";
        };
        
        this.connect = (email) => {
            const url = this.base_url + "/token/generate?email=" + encodeURIComponent(email);
            const req = new XMLHttpRequest();
            req.overrideMimeType("application/json");
            var cb = this.handleResponse;
            req.open("GET", url, false);
            req.onload = function () {
                cb(req.responseText);
            };
            req.send();
        };
        this.refresh = () => {
            const identity = this.getIdentity();
            if (identity) {
                const url = this.base_url + "/token/refresh?refresh_token=" + encodeURIComponent(identity["refresh_token"]);
                const req = new XMLHttpRequest();
                req.overrideMimeType("application/json");
                var cb = this.handleResponse;
                req.open("GET", url, false);
                req.onload = function () {
                    cb(req.responseText);
                };
                req.send();
            }
        };
        this.disconnect = () => {
            this.removeCookie("__uid_2");
        };
    }
}
window.__uid2 = new UID2();
