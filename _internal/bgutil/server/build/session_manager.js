import axios from "axios";
import { BG, buildURL, getHeaders, USER_AGENT, } from "bgutils-js";
import { Agent } from "node:https";
import { ProxyAgent } from "proxy-agent";
import { JSDOM } from "jsdom";
import { Innertube } from "youtubei.js";
class Logger {
    debug;
    log;
    warn;
    error;
    constructor(shouldLog = true) {
        if (shouldLog) {
            this.debug = (msg) => {
                console.debug(msg);
            };
            this.log = (msg) => {
                console.log(msg);
            };
        }
        else {
            this.debug = this.log = () => { };
        }
        this.warn = (msg) => {
            console.warn(msg);
        };
        this.error = (msg) => {
            console.error(msg);
        };
    }
}
class ProxySpec {
    proxyUrl;
    sourceAddress;
    disableTlsVerification = false;
    ipFamily;
    constructor({ sourceAddress, disableTlsVerification }) {
        this.sourceAddress = sourceAddress;
        this.disableTlsVerification = disableTlsVerification || false;
        if (!this.sourceAddress) {
            this.ipFamily = undefined;
        }
        else {
            this.ipFamily = this.sourceAddress?.includes(":") ? 6 : 4;
        }
    }
    get proxy() {
        return this.proxyUrl?.href;
    }
    set proxy(newProxy) {
        if (newProxy) {
            // Normalize and sanitize the proxy URL
            try {
                this.proxyUrl = new URL(newProxy);
            }
            catch {
                newProxy = `http://${newProxy}`;
                try {
                    this.proxyUrl = new URL(newProxy);
                }
                catch (e) {
                    throw new Error(`Invalid proxy URL: ${newProxy}`, {
                        cause: e,
                    });
                }
            }
        }
    }
    asDispatcher(logger) {
        const { proxyUrl, sourceAddress, disableTlsVerification } = this;
        if (!proxyUrl) {
            return new Agent({
                localAddress: sourceAddress,
                family: this.ipFamily,
                rejectUnauthorized: !disableTlsVerification,
            });
        }
        // Proxy must be a string as long as the URL is truthy
        const pxyStr = this.proxy;
        const { password } = proxyUrl;
        const loggedProxy = password
            ? pxyStr.replace(password, "****")
            : pxyStr;
        logger.log(`Using proxy: ${loggedProxy}`);
        try {
            return new ProxyAgent({
                getProxyForUrl: () => pxyStr,
                localAddress: sourceAddress,
                family: this.ipFamily,
                rejectUnauthorized: !disableTlsVerification,
            });
        }
        catch (e) {
            throw new Error(`Failed to create proxy agent for ${loggedProxy}`, {
                cause: e,
            });
        }
    }
}
class CacheSpec {
    pxySpec;
    ip;
    constructor(pxySpec, ip) {
        this.pxySpec = pxySpec;
        this.ip = ip;
    }
    get key() {
        return JSON.stringify(this.ip || [this.pxySpec.proxy, this.pxySpec.sourceAddress]);
    }
}
export class SessionManager {
    youtubeSessionDataCaches;
    // hardcoded API key that has been used by youtube for years
    static REQUEST_KEY = "O43z0dpjhgX20SCx4KAo";
    static hasDom = false;
    _minterCache = new Map();
    TOKEN_TTL_HOURS;
    logger;
    constructor(shouldLog = true, 
    // This needs to be reworked as POTs are IP-bound
    youtubeSessionDataCaches) {
        this.youtubeSessionDataCaches = youtubeSessionDataCaches;
        this.logger = new Logger(shouldLog);
        this.TOKEN_TTL_HOURS = process.env.TOKEN_TTL
            ? parseInt(process.env.TOKEN_TTL)
            : 6;
        if (!SessionManager.hasDom) {
            const dom = new JSDOM('<!DOCTYPE html><html lang="en"><head><title></title></head><body></body></html>', {
                url: "https://www.youtube.com/",
                referrer: "https://www.youtube.com/",
                userAgent: USER_AGENT,
            });
            Object.assign(globalThis, {
                window: dom.window,
                document: dom.window.document,
                location: dom.window.location,
                origin: dom.window.origin,
            });
            if (!Reflect.has(globalThis, "navigator")) {
                Object.defineProperty(globalThis, "navigator", {
                    value: dom.window.navigator,
                });
            }
            SessionManager.hasDom = true;
        }
    }
    invalidateCaches() {
        this.setYoutubeSessionDataCaches();
        this._minterCache.clear();
    }
    invalidateIT() {
        this._minterCache.forEach((minterCache) => {
            minterCache.expiry = new Date(0);
        });
    }
    cleanupCaches() {
        for (const contentBinding in this.youtubeSessionDataCaches) {
            const sessionData = this.youtubeSessionDataCaches[contentBinding];
            if (sessionData && new Date() > sessionData.expiresAt)
                delete this.youtubeSessionDataCaches[contentBinding];
        }
    }
    getYoutubeSessionDataCaches(cleanup = false) {
        if (cleanup)
            this.cleanupCaches();
        return this.youtubeSessionDataCaches;
    }
    setYoutubeSessionDataCaches(youtubeSessionData) {
        this.youtubeSessionDataCaches = youtubeSessionData;
    }
    get minterCache() {
        return this._minterCache;
    }
    async getDescrambledChallenge(bgConfig, challenge, innertubeContext) {
        try {
            if (!challenge) {
                this.logger.debug("Using challenge from /att/get");
                const attGetResponse = await bgConfig.fetch("https://www.youtube.com/youtubei/v1/att/get?prettyPrint=false", {
                    method: "POST",
                    headers: {
                        ...getHeaders(),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        context: innertubeContext || {
                            client: {
                                clientName: "WEB",
                                clientVersion: "2.20260227.01.00",
                            },
                        },
                        engagementType: "ENGAGEMENT_TYPE_UNBOUND",
                    }),
                });
                const attestation = await attGetResponse.json();
                if (!attestation)
                    throw new Error("Failed to get challenge from /att/get");
                challenge = attestation.bgChallenge;
            }
            else {
                this.logger.debug("Using challenge from the webpage");
            }
            const { program, globalName, interpreterHash } = challenge;
            const { privateDoNotAccessOrElseTrustedResourceUrlWrappedValue } = challenge.interpreterUrl;
            const interpreterJSResponse = await bgConfig.fetch(`https:${privateDoNotAccessOrElseTrustedResourceUrlWrappedValue}`);
            const interpreterJS = await interpreterJSResponse.text();
            return {
                program,
                globalName,
                interpreterHash,
                interpreterJavascript: {
                    privateDoNotAccessOrElseSafeScriptWrappedValue: interpreterJS,
                    privateDoNotAccessOrElseTrustedResourceUrlWrappedValue,
                },
            };
        }
        catch (e) {
            throw new Error("Could not get BotGuard challenge", { cause: e });
        }
    }
    async generateTokenMinter(cacheSpec, bgConfig, challenge, innertubeContext) {
        const descrambledChallenge = await this.getDescrambledChallenge(bgConfig, challenge, innertubeContext);
        const { program, globalName } = descrambledChallenge;
        const interpreterJavascript = descrambledChallenge.interpreterJavascript
            .privateDoNotAccessOrElseSafeScriptWrappedValue;
        if (interpreterJavascript) {
            new Function(interpreterJavascript)();
        }
        else
            throw new Error("Could not load VM");
        let bgClient;
        try {
            bgClient = await BG.BotGuardClient.create({
                program,
                globalName,
                globalObj: bgConfig.globalObj,
            });
        }
        catch (e) {
            throw new Error(`Failed to create BG client.`, { cause: e });
        }
        try {
            const webPoSignalOutput = [];
            const botguardResponse = await bgClient.snapshot({
                webPoSignalOutput,
            });
            const integrityTokenResp = await bgConfig.fetch(buildURL("GenerateIT"), {
                method: "POST",
                headers: getHeaders(),
                body: JSON.stringify([
                    SessionManager.REQUEST_KEY,
                    botguardResponse,
                ]),
            });
            const [integrityToken, estimatedTtlSecs, mintRefreshThreshold, websafeFallbackToken,] = (await integrityTokenResp.json());
            const integrityTokenData = {
                integrityToken,
                estimatedTtlSecs,
                mintRefreshThreshold,
                websafeFallbackToken,
            };
            if (!integrityToken)
                throw new Error(`Unexpected empty integrity token, response: ${JSON.stringify(integrityTokenData)}`);
            this.logger.debug(`Generated IntegrityToken: ${JSON.stringify(integrityTokenData)}`);
            const tokenMinter = {
                expiry: new Date(Date.now() + estimatedTtlSecs * 1000),
                integrityToken,
                minter: await BG.WebPoMinter.create(integrityTokenData, webPoSignalOutput),
            };
            this._minterCache.set(cacheSpec.key, tokenMinter);
            return tokenMinter;
        }
        catch (e) {
            throw new Error(`Failed to generate an integrity token.`, {
                cause: e,
            });
        }
    }
    async tryMintPOT(contentBinding, tokenMinter) {
        this.logger.log(`Generating POT for ${contentBinding}`);
        try {
            const poToken = await tokenMinter.minter.mintAsWebsafeString(contentBinding);
            if (poToken) {
                this.logger.log(`poToken: ${poToken}`);
                const youtubeSessionData = {
                    contentBinding,
                    poToken,
                    expiresAt: new Date(Date.now() + this.TOKEN_TTL_HOURS * 60 * 60 * 1000),
                };
                if (this.youtubeSessionDataCaches)
                    this.youtubeSessionDataCaches[contentBinding] =
                        youtubeSessionData;
                return youtubeSessionData;
            }
            else
                throw new Error("Unexpected empty POT");
        }
        catch (e) {
            throw new Error(`Failed to mint POT for ${contentBinding}: ${e.message}`, { cause: e });
        }
    }
    getFetch(proxySpec, maxRetries, intervalMs) {
        const { logger } = this;
        return async (url, options) => {
            const method = (options?.method || "GET").toUpperCase();
            for (let attempts = 1; attempts <= maxRetries; attempts++) {
                try {
                    const axiosOpt = {
                        headers: options?.headers,
                        params: options?.params,
                        httpsAgent: proxySpec.asDispatcher(logger),
                    };
                    const response = await (method === "GET"
                        ? axios.get(url, axiosOpt)
                        : axios.post(url, options?.body, axiosOpt));
                    return {
                        ok: response.status >= 200 && response.status < 300,
                        status: response.status,
                        json: async () => response.data,
                        text: async () => typeof response.data === "string"
                            ? response.data
                            : JSON.stringify(response.data),
                    };
                }
                catch (e) {
                    if (attempts >= maxRetries)
                        throw new Error(`Error reaching ${method} ${url}: All ${attempts} retries failed.`, { cause: e });
                    await new Promise((resolve) => setTimeout(resolve, intervalMs));
                }
            }
        };
    }
    async generatePoToken(contentBinding, proxy = "", bypassCache = false, sourceAddress = undefined, disableTlsVerification = false, challenge = undefined, innertubeContext) {
        this.cleanupCaches();
        const pxySpec = new ProxySpec({
            sourceAddress,
            disableTlsVerification,
        });
        if (proxy) {
            pxySpec.proxy = proxy;
        }
        else {
            pxySpec.proxy =
                process.env.HTTPS_PROXY ||
                    process.env.HTTP_PROXY ||
                    process.env.ALL_PROXY;
        }
        const cacheSpec = new CacheSpec(pxySpec, innertubeContext?.client.remoteHost || null);
        const bgFetch = this.getFetch(pxySpec, 3, 5000);
        let innertube = undefined;
        if (!contentBinding && innertubeContext) {
            this.logger.warn("No content binding provided, using the one from the supplied Innertube context...");
            contentBinding = innertubeContext.client.visitorData;
        }
        if (!contentBinding) {
            this.logger.warn("No content binding provided, generating visitor data via Innertube...");
            innertube = await Innertube.create({
                retrieve_player: false,
                fetch: bgFetch,
            });
            contentBinding = innertube.session.context.client.visitorData;
        }
        if (!contentBinding)
            throw new Error("Unable to generate visitor data");
        if (!innertubeContext)
            innertubeContext = innertube?.session.context;
        const bgConfig = {
            fetch: bgFetch,
            globalObj: globalThis,
            identifier: contentBinding,
            requestKey: SessionManager.REQUEST_KEY,
        };
        if (!bypassCache) {
            if (this.youtubeSessionDataCaches) {
                const sessionData = this.youtubeSessionDataCaches[contentBinding];
                if (sessionData) {
                    this.logger.log(`POT for ${contentBinding} still fresh, returning cached token`);
                    return sessionData;
                }
            }
            let tokenMinter = this._minterCache.get(cacheSpec.key);
            if (tokenMinter) {
                // Replace minter if expired
                if (new Date() >= tokenMinter.expiry) {
                    this.logger.log("POT minter expired, getting a new one");
                    tokenMinter = await this.generateTokenMinter(cacheSpec, bgConfig, challenge, innertubeContext);
                }
                return await this.tryMintPOT(contentBinding, tokenMinter);
            }
        }
        const tokenMinter = await this.generateTokenMinter(cacheSpec, bgConfig, challenge, innertubeContext);
        return await this.tryMintPOT(contentBinding, tokenMinter);
    }
}
//# sourceMappingURL=session_manager.js.map