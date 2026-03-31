import { Parser } from '../index.js';
import GuideSection from '../classes/GuideSection.js';
import GuideSubscriptionsSection from '../classes/GuideSubscriptionsSection.js';
export default class Guide {
    #page;
    contents;
    constructor(data) {
        this.#page = Parser.parseResponse(data);
        if (this.#page.items)
            this.contents = this.#page.items.array().as(GuideSection, GuideSubscriptionsSection);
    }
    get page() {
        return this.#page;
    }
}
//# sourceMappingURL=Guide.js.map