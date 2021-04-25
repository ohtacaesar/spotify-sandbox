import React, {SyntheticEvent} from 'react';
import './App.css';
import {TrackTable} from './Track'

export const BASE_URL = 'http://localhost:8000'

interface AppProps {
}

interface AppState {
  inProgress: boolean;
}

class App extends React.Component<AppProps, AppState> {
  constructor(props: AppProps) {
    super(props);
    this.state = {inProgress: false};
  }

  replacePlaylist = (e: SyntheticEvent) => {
    if (this.state.inProgress) {
      return;
    }

    this.setState({inProgress: true})
    fetch(BASE_URL + '/replace_playlist', {
      method: 'POST'
    }).then((r) => {
      this.setState({inProgress: false})
    })
  }

  render() {
    return <div className="App">
      <button
          onClick={this.replacePlaylist}
          disabled={this.state.inProgress}>プレイリスト更新
      </button>
      <TrackTable/>
    </div>
  }
}


export default App;
