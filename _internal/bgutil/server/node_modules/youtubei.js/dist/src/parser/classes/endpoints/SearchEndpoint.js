import { YTNode } from '../../helpers.js';
const API_PATH = 'search';
export default class SearchEndpoint extends YTNode {
    static type = 'SearchEndpoint';
    #data;
    constructor(data) {
        super();
        this.#data = data;
    }
    getApiPath() {
        return API_PATH;
    }
    buildRequest() {
        const request = {};
        if (this.#data.query)
            request.query = this.#data.query;
        if (this.#data.params)
            request.params = this.#data.params;
        if (this.#data.webSearchboxStatsUrl)
            request.webSearchboxStatsUrl = this.#data.webSearchboxStatsUrl;
        if (this.#data.suggestStats)
            request.suggestStats = this.#data.suggestStats;
        return request;
    }
}
//# sourceMappingURL=SearchEndpoint.js.map