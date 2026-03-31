import { Parser } from '../index.js';
import { InnertubeError } from '../../utils/Utils.js';
import AccountSectionList from '../classes/AccountSectionList.js';
export default class AccountInfo {
    #page;
    contents;
    constructor(response) {
        this.#page = Parser.parseResponse(response.data);
        if (!this.#page.contents)
            throw new InnertubeError('Page contents not found');
        const account_section_list = this.#page.contents.array().as(AccountSectionList)[0];
        if (!account_section_list)
            throw new InnertubeError('Account section list not found');
        this.contents = account_section_list.contents[0];
    }
    get page() {
        return this.#page;
    }
}
//# sourceMappingURL=AccountInfo.js.map