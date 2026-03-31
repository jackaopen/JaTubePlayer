import { YTNode } from '../../helpers.js';
const API_PATH = 'kids/get_kids_blocklist_picker';
export default class GetKidsBlocklistPickerCommand extends YTNode {
    static type = 'GetKidsBlocklistPickerCommand';
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
        if (this.#data.blockedForKidsContent)
            request.blockedForKidsContent = this.#data.blockedForKidsContent;
        return request;
    }
}
//# sourceMappingURL=GetKidsBlocklistPickerCommand.js.map