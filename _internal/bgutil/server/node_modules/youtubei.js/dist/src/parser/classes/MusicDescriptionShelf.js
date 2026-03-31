import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class MusicDescriptionShelf extends YTNode {
    static type = 'MusicDescriptionShelf';
    description;
    max_collapsed_lines;
    max_expanded_lines;
    footer;
    constructor(data) {
        super();
        this.description = new Text(data.description);
        if (Reflect.has(data, 'maxCollapsedLines')) {
            this.max_collapsed_lines = data.maxCollapsedLines;
        }
        if (Reflect.has(data, 'maxExpandedLines')) {
            this.max_expanded_lines = data.maxExpandedLines;
        }
        this.footer = new Text(data.footer);
    }
}
//# sourceMappingURL=MusicDescriptionShelf.js.map