<template>
  <div class="row g-4">
    <div class="col-lg-5">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body d-flex flex-column">
          <h5 class="fw-semibold mb-3">Support tickets</h5>
          <div class="ticket-form mb-4">
            <form @submit.prevent="handleCreateTicket" class="d-flex flex-column gap-2">
              <input v-model="ticketSubject" type="text" class="form-control" placeholder="Subject" required />
              <textarea v-model="ticketDescription" class="form-control" rows="3" placeholder="Describe your issue" required></textarea>
              <button type="submit" class="btn btn-primary" :disabled="creatingTicket">
                <span v-if="creatingTicket" class="spinner-border spinner-border-sm me-2"></span>
                Create ticket
              </button>
            </form>
          </div>
          <div class="list-group overflow-auto" style="max-height: 360px;">
            <div
              v-for="ticket in tickets"
              :key="ticket.id"
              class="list-group-item list-group-item-action"
              :class="{ active: selectedTicket?.id === ticket.id }"
              role="button"
              @click="selectedTicket = ticket"
            >
              <div class="d-flex justify-content-between">
                <span class="fw-semibold">{{ ticket.subject }}</span>
                <span class="badge bg-light text-dark text-uppercase">{{ ticket.status }}</span>
              </div>
              <p class="text-muted small mb-0">{{ ticket.description }}</p>
            </div>
            <p v-if="!tickets.length" class="text-muted text-center py-3">No tickets yet.</p>
          </div>
        </div>
      </div>
    </div>

    <div class="col-lg-7">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body d-flex flex-column">
          <h5 class="fw-semibold mb-3">Live support chat</h5>
          <div class="chat-window flex-grow-1 border rounded p-3 mb-3 overflow-auto">
            <div v-for="message in messages" :key="message.id" class="mb-3">
              <div class="d-flex justify-content-between">
                <span class="fw-semibold">{{ message.author.username }}</span>
                <small class="text-muted">{{ formatDate(message.createdAt) }}</small>
              </div>
              <p class="mb-0">{{ message.content }}</p>
            </div>
            <p v-if="!messages.length" class="text-muted">Start the conversation with a question.</p>
          </div>
          <form @submit.prevent="handleSendMessage" class="d-flex gap-2">
            <input v-model="chatMessage" type="text" class="form-control" placeholder="Type a message" required />
            <button type="submit" class="btn btn-primary" :disabled="sendingMessage">
              <span v-if="sendingMessage" class="spinner-border spinner-border-sm me-2"></span>
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { gql } from '@apollo/client/core';
import { useMutation, useQuery } from '@vue/apollo-composable';

const SUPPORT_QUERY = gql`
  query SupportCenter {
    supportTickets {
      id
      subject
      description
      status
    }
    chatMessages {
      id
      content
      createdAt
      author {
        username
      }
    }
  }
`;

const CREATE_TICKET_MUTATION = gql`
  mutation CreateTicket($subject: String!, $description: String!) {
    createSupportTicket(subject: $subject, description: $description) {
      ticket {
        id
        subject
        description
        status
      }
    }
  }
`;

const POST_MESSAGE_MUTATION = gql`
  mutation PostMessage($message: String!) {
    postChatMessage(message: $message) {
      chatMessage {
        id
        content
        createdAt
        author {
          username
        }
      }
    }
  }
`;

const ticketSubject = ref('');
const ticketDescription = ref('');
const chatMessage = ref('');
const creatingTicket = ref(false);
const sendingMessage = ref(false);
const selectedTicket = ref<any | null>(null);

const { result, refetch, loading } = useQuery(SUPPORT_QUERY, undefined, { fetchPolicy: 'network-only' });

const tickets = computed(() => result.value?.supportTickets ?? []);
const messages = computed(() => result.value?.chatMessages ?? []);

const { mutate: createTicket } = useMutation(CREATE_TICKET_MUTATION);
const { mutate: postMessage } = useMutation(POST_MESSAGE_MUTATION);

async function handleCreateTicket() {
  creatingTicket.value = true;
  try {
    await createTicket({ subject: ticketSubject.value, description: ticketDescription.value });
    ticketSubject.value = '';
    ticketDescription.value = '';
    await refetch();
  } finally {
    creatingTicket.value = false;
  }
}

async function handleSendMessage() {
  sendingMessage.value = true;
  try {
    await postMessage({ message: chatMessage.value });
    chatMessage.value = '';
    await refetch();
  } finally {
    sendingMessage.value = false;
  }
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(date));
}
</script>

