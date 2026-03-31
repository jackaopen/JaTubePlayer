import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
export default class CommandExecutorCommand extends YTNode {
    static type = 'CommandExecutorCommand';
    commands;
    constructor(data) {
        super();
        this.commands = Parser.parseCommands(data.commands);
    }
}
//# sourceMappingURL=CommandExecutorCommand.js.map