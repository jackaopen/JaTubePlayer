import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class Quiz extends YTNode {
    static type = 'Quiz';
    choices;
    total_votes;
    constructor(data) {
        super();
        this.choices = data.choices.map((choice) => ({
            text: new Text(choice.text),
            is_correct: choice.isCorrect
        }));
        this.total_votes = new Text(data.totalVotes);
    }
}
//# sourceMappingURL=Quiz.js.map