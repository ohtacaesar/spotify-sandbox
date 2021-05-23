import React from "react";
import {JwtContext} from "../../../contexts/JwtContext";
import {BASE_URL} from "../../pages/App";

interface ReplacePlaylistButtonState {
  inProgress: boolean;
}

export class ReplacePlaylistButton extends React.Component<any, ReplacePlaylistButtonState> {
  static contextType = JwtContext;

  constructor(props: any) {
    super(props);
    this.state = {
      inProgress: false
    }
  }

  replacePlaylist = () => {
    if (this.state.inProgress) {
      return;
    }

    this.setState({inProgress: true});
    fetch(BASE_URL + '/replace_playlist', {
      method: 'POST',
      headers: {Authorization: `Bearer ${this.context}`}
    }).then((r) => {
    }).finally(() => this.setState({inProgress: false}))
  }

  render() {
    return <button
        onClick={() => this.replacePlaylist()}
        disabled={this.state.inProgress}>プレイリスト更新
    </button>
  }
}

