import React from "react";
import {JwtContext} from "../../../../contexts/JwtContext";
import {BASE_URL} from "../../App";
import {UserArtist} from "../ArtistRow";

export class UserTrack {
  id: string;
  name: string;
  userArtists: UserArtist[];
  blocked: boolean;

  constructor(id: string, name: string, userArtists: UserArtist[], blocked: boolean) {
    this.id = id;
    this.name = name;
    this.userArtists = userArtists;
    this.blocked = blocked;
  }

  isBlocked(): boolean {
    return this.blocked || this.userArtists.some((v) => v.blocked);
  }
}


interface Props {
  rank: number;
  userTrack: UserTrack;
  updateParent: Function;
}

interface State {
  inProgress: boolean;
}


export class TrackRow extends React.Component<Props, State> {
  static contextType = JwtContext;

  constructor(props: Props) {
    super(props);
    this.state = {inProgress: false}
  }

  put(trackId: string, mute: boolean) {
    if (this.state.inProgress) {
      return;
    }
    this.setState({inProgress: true})
    const url = `${BASE_URL}/tracks/${trackId}`;
    fetch(url, {
      method: 'PUT',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${this.context}`,
      },
      body: JSON.stringify({mute: mute})
    }).then(() => {
      this.props.userTrack.blocked = mute;
      this.props.updateParent();
    }).finally(() => {
      this.setState({inProgress: false})
    })
  }

  render() {
    const userTrack = this.props.userTrack;
    let button;
    if (userTrack.blocked) {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.put(userTrack.id, false)}>ミュート解除</button>;
    } else {
      button = <button
          disabled={this.state.inProgress}
          onClick={() => this.put(userTrack.id, true)}>ミュート</button>;
    }

    return (
        <tr key={userTrack.id}
            style={{backgroundColor: userTrack.isBlocked() ? '#cccccc' : ''}}>
          <td>{this.props.rank}</td>
          <td>{userTrack.name}</td>
          <td>{userTrack.userArtists.map((a) => a.name).join(", ")}</td>
          <td>{button}</td>
        </tr>
    )
  }
}
