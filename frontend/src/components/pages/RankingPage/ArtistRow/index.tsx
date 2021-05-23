import React from "react";
import {JwtContext} from "../../../../contexts/JwtContext";
import {BASE_URL} from "../../App";

export class UserArtist {
  id: string;
  name: string;
  blocked: boolean;

  constructor(id: string, name: string, blocked: boolean) {
    this.id = id;
    this.name = name;
    this.blocked = blocked;
  }

  isBlocked() {
    return this.blocked;
  }
}

interface Props {
  userArtist: UserArtist;
  updateParent: Function;
}

interface State {
  inProgress: boolean;
}

export class ArtistRow extends React.Component<Props, State> {
  static contextType = JwtContext;

  constructor(props: Props) {
    super(props);
    this.state = {inProgress: false};
  }

  put(artistId: string, mute: boolean) {
    if (this.state.inProgress) {
      return;
    }
    this.setState({inProgress: true})
    const url = `${BASE_URL}/artists/${artistId}`;
    fetch(url, {
      method: 'PUT',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${this.context}`,
      },
      body: JSON.stringify({mute: mute}),
    }).then(() => {
      this.props.userArtist.blocked = mute;
      this.props.updateParent();
    }).finally(() => {
      this.setState({inProgress: false})
    })
  }

  render() {
    const userArtist = this.props.userArtist;
    let button;
    if (!userArtist.blocked) {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.put(userArtist.id, true)}>ミュート</button>;
    } else {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.put(userArtist.id, false)}>ミュート解除</button>;
    }

    return <tr
        key={userArtist.id}
        style={{backgroundColor: userArtist.isBlocked() ? '#cccccc' : ''}}>
      <td>{userArtist.name}</td>
      <td>{button}</td>
    </tr>
  }
}
