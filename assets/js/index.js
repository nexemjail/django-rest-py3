let React = require('react')
let ReactDOM = require('react-dom')

function Square(props){
    return (
      <button className="square" onClick={() => props.onClick()}>
        {props.value}
      </button>
    )
}


class Board extends React.Component {
  renderSquare(i) {
    return <Square value={this.props.squares[i]} onClick={() => this.props.onClick(i)} />
  }

  render() {
    return (
      <div className="board">
        <div className="row">
          {this.renderSquare(0)}
          {this.renderSquare(1)}
          {this.renderSquare(2)}
        </div>
        <div className="row">
          {this.renderSquare(3)}
          {this.renderSquare(4)}
          {this.renderSquare(5)}
        </div>
        <div className="row">
          {this.renderSquare(6)}
          {this.renderSquare(7)}
          {this.renderSquare(8)}
        </div>
      </div>
    )
  }
}

class Game extends React.Component {
  constructor() {
    super();
    this.state = {
      history: [{
        squares : Array(9).fill(null),
      }],
      stepNumber : 0,
      xIsNext: true
    }
  }

  calculateWinner(squares) {
    const lines = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ];
    for (let i = 0; i < lines.length; i++) {
      const [a, b, c] = lines[i];
      if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
        return squares[a];
      }
    }
    return null;
  }

  handleClick(i) {
    const history = this.state.history.slice(0, this.state.stepNumber + 1);
    const current = history[history.length - 1];
    const squares = current.squares.slice();
    if (this.calculateWinner(squares) || squares[i]) {
      return;
    }
    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
      history: history.concat([{
        squares: squares
      }]),
      stepNumber : history.length,
      xIsNext: !this.state.xIsNext,
    });
  }

  jumpTo(step) {
    this.setState({
      stepNumber: step,
      xIsNext: (step % 2) ? false : true
    })
  }

  render() {
    const history = this.state.history
    const current = history[this.state.stepNumber]
    console.log(history, this.state.stepNumber)
    const winner = this.calculateWinner(current.squares)

    let status;
    if (winner) {
      status = 'Winner: ' + winner
    } else {
      status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O')
    }

    const moves = history.map((step, move) => {
      const desc = move ? 'Move #' + move : 'Game start!'
      return (
        <li>
          <a href='#' onClick={() => this.jumpTo(move)}>{desc}</a>
        </li>
      )
    });

    return (
      <div>
        <div className="game">
          <Board squares={current.squares} onClick={(i) => this.handleClick(i)}/>
        </div>
        <div className="info">
          <div>{status}</div>
          <ol>{moves}</ol>
        </div>
      </div>
    )
  }

}

ReactDOM.render(<Game />, document.getElementById('container'))
