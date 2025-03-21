import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from ".";
import axios from "axios";
import { setCSRFToken } from '../utils/csrfUtils';

// Define types for the state
interface Member {
  user: string;
  role: string;
}

interface Invitation {
  email: string;
  accepted: boolean;
}

interface Organization {
  members: Member[];
  invitations: Invitation[];
}

interface OrganizationsState {
  organizations: { [key: string]: Organization };
  loading: boolean;
  invite_sent: boolean;
  error: string | null;
  refetch: boolean;
}

// Initial state
const initialState: OrganizationsState = {
  organizations: {},
  loading: false,
  invite_sent: false,
  error: null,
  refetch: false,
};


// Configure Axios globally for JSON requests
axios.defaults.headers.common["Content-Type"] = "application/json";

// Async thunk for fetching organizations
export const fetchOrganizations = createAsyncThunk(
  "organizations/fetchOrganizations",
  async () => {
    setCSRFToken();
    const response = await axios.get("/api/organizations");
    return response.data as { [key: string]: Organization };
  }
);

// Async thunk for inviting a member to an organization
export const inviteMemberThunk = createAsyncThunk(
  "organizations/inviteMember",
  async ({ orgKey, email, message }: { orgKey: number; email: string; message: string }) => {
    setCSRFToken();
    try {
      const response = await axios.post(`/api/organization/${orgKey}/invite/`, {
        email,
        message,
      });
      return { orgKey, email }; // Return success response
    } catch (error: any) {
      // If the error is caught, throw a custom error
      throw new Error(error.response?.data?.error || "Failed to send invitation.");
    }
  }
);


// Async thunk for deleting a member from an organization
export const deleteMember = createAsyncThunk(
  "organizations/deleteMember",
  async ({ orgKey, user }: { orgKey: string; user: string }) => {
    setCSRFToken();
    const response = await axios.delete(`/api/organizations/member/delete/`, {
      data: {
        organisation_id: orgKey,
        user_email: user,
      },
    });
    return { orgKey, user };
  }
);

// Slice
const organizationsSlice = createSlice({
  name: "organizations",
  initialState,
  reducers: {
    clearResponseMessage: (state) => {
      state.error = null;
      state.invite_sent = false;
    },
    addMember: (state, action: PayloadAction<{ orgKey: string; member: Member }>) => {
      const { orgKey, member } = action.payload;
      state.organizations[orgKey]?.members.push(member);
    },
    deleteMemberFromState: (state, action: PayloadAction<{ orgKey: string; user: string }>) => {
      const { orgKey, user } = action.payload;
      state.organizations[orgKey].members = state.organizations[orgKey]?.members.filter(
        (member) => member.user !== user
      );
    },
    updateState: (state, action: PayloadAction<{ orgKey: string; email: string; message: string }>) => {
      const { orgKey, email, message } = action.payload;
      const newInvitation: Invitation = {
        email,
        accepted: false,
      };
      if (!state.organizations[orgKey]) {
          state.organizations[orgKey] = { members: [], invitations: [] };
      }
      state.organizations[orgKey].invitations.push(newInvitation);
    },
    resetRefetch: (state) => {
      state.refetch = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrganizations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrganizations.fulfilled, (state, action) => {
        state.organizations = action.payload;
        state.loading = false;
        state.refetch = false;
      })
      .addCase(fetchOrganizations.rejected, (state, action) => {
        state.error = action.error.message || "Failed to fetch data.";
        state.loading = false;
        state.organizations = {};
      })
      .addCase(inviteMemberThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.invite_sent = false;
      })
      .addCase(inviteMemberThunk.fulfilled, (state, action) => {
        const { orgKey, email } = action.payload;
        if (!state.organizations[orgKey]) {
          state.organizations[orgKey] = { members: [], invitations: [] };
        }
        const invitation: Invitation = { email, accepted: false };
        state.organizations[orgKey]?.invitations.push(invitation);
        state.loading = false;
        state.refetch = true;
        state.invite_sent = true;
      })
      .addCase(inviteMemberThunk.rejected, (state, action) => {
        state.error = action.error.message || "Failed to send invitation.";
        state.loading = false;
        state.invite_sent = false
      })
      .addCase(deleteMember.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteMember.fulfilled, (state, action) => {
        const { orgKey, user } = action.payload;
        state.loading = false;
        state.refetch = true;
      })
      .addCase(deleteMember.rejected, (state, action) => {
        state.error = action.error.message || "Failed to delete member.";
        state.loading = false;
      });
  },
});

export const selectRefetch = (state: RootState) => state.organization.refetch;
export const { addMember, deleteMemberFromState, updateState, resetRefetch, clearResponseMessage } = organizationsSlice.actions;
export default organizationsSlice.reducer;
 