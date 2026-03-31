import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
export default class ShowingResultsFor extends YTNode {
    static type = 'ShowingResultsFor';
    corrected_query;
    original_query;
    corrected_query_endpoint;
    original_query_endpoint;
    search_instead_for;
    showing_results_for;
    constructor(data) {
        super();
        this.corrected_query = new Text(data.correctedQuery);
        this.original_query = new Text(data.originalQuery);
        this.corrected_query_endpoint = new NavigationEndpoint(data.correctedQueryEndpoint);
        this.original_query_endpoint = new NavigationEndpoint(data.originalQueryEndpoint);
        this.search_instead_for = new Text(data.searchInsteadFor);
        this.showing_results_for = new Text(data.showingResultsFor);
    }
}
//# sourceMappingURL=ShowingResultsFor.js.map