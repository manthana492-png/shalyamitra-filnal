export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      alerts: {
        Row: {
          acknowledged: boolean
          acknowledged_at: string | null
          acknowledged_by: string | null
          body: string
          created_at: string
          id: string
          session_id: string
          severity: Database["public"]["Enums"]["alert_severity"]
          source: string | null
          title: string
        }
        Insert: {
          acknowledged?: boolean
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          body: string
          created_at?: string
          id?: string
          session_id: string
          severity?: Database["public"]["Enums"]["alert_severity"]
          source?: string | null
          title: string
        }
        Update: {
          acknowledged?: boolean
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          body?: string
          created_at?: string
          id?: string
          session_id?: string
          severity?: Database["public"]["Enums"]["alert_severity"]
          source?: string | null
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "alerts_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      audit_log: {
        Row: {
          action: string
          actor_email: string | null
          actor_id: string | null
          created_at: string
          details: Json
          id: string
          session_id: string | null
        }
        Insert: {
          action: string
          actor_email?: string | null
          actor_id?: string | null
          created_at?: string
          details?: Json
          id?: string
          session_id?: string | null
        }
        Update: {
          action?: string
          actor_email?: string | null
          actor_id?: string | null
          created_at?: string
          details?: Json
          id?: string
          session_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "audit_log_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string
          full_name: string | null
          hospital: string | null
          id: string
          title: string | null
          updated_at: string
          user_id: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          full_name?: string | null
          hospital?: string | null
          id?: string
          title?: string | null
          updated_at?: string
          user_id: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          full_name?: string | null
          hospital?: string | null
          id?: string
          title?: string | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      sessions: {
        Row: {
          anaesthetist_name: string | null
          created_at: string
          created_by: string
          current_mode: Database["public"]["Enums"]["aria_mode"]
          disclaimer_accepted: boolean
          disclaimer_accepted_at: string | null
          ended_at: string | null
          id: string
          notes: string | null
          patient_code: string
          procedure_category: string | null
          procedure_name: string
          started_at: string | null
          status: Database["public"]["Enums"]["session_status"]
          surgeon_name: string | null
          theatre: string | null
          updated_at: string
        }
        Insert: {
          anaesthetist_name?: string | null
          created_at?: string
          created_by: string
          current_mode?: Database["public"]["Enums"]["aria_mode"]
          disclaimer_accepted?: boolean
          disclaimer_accepted_at?: string | null
          ended_at?: string | null
          id?: string
          notes?: string | null
          patient_code: string
          procedure_category?: string | null
          procedure_name: string
          started_at?: string | null
          status?: Database["public"]["Enums"]["session_status"]
          surgeon_name?: string | null
          theatre?: string | null
          updated_at?: string
        }
        Update: {
          anaesthetist_name?: string | null
          created_at?: string
          created_by?: string
          current_mode?: Database["public"]["Enums"]["aria_mode"]
          disclaimer_accepted?: boolean
          disclaimer_accepted_at?: string | null
          ended_at?: string | null
          id?: string
          notes?: string | null
          patient_code?: string
          procedure_category?: string | null
          procedure_name?: string
          started_at?: string | null
          status?: Database["public"]["Enums"]["session_status"]
          surgeon_name?: string | null
          theatre?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      transcripts: {
        Row: {
          created_at: string
          id: string
          redacted: boolean
          session_id: string
          speaker: Database["public"]["Enums"]["transcript_speaker"]
          spoken_at: string
          text: string
        }
        Insert: {
          created_at?: string
          id?: string
          redacted?: boolean
          session_id: string
          speaker: Database["public"]["Enums"]["transcript_speaker"]
          spoken_at?: string
          text: string
        }
        Update: {
          created_at?: string
          id?: string
          redacted?: boolean
          session_id?: string
          speaker?: Database["public"]["Enums"]["transcript_speaker"]
          spoken_at?: string
          text?: string
        }
        Relationships: [
          {
            foreignKeyName: "transcripts_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      user_roles: {
        Row: {
          created_at: string
          id: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _user_id: string
        }
        Returns: boolean
      }
      is_admin: { Args: { _user_id: string }; Returns: boolean }
    }
    Enums: {
      alert_severity: "info" | "caution" | "warning" | "critical"
      app_role: "admin" | "surgeon" | "anaesthetist"
      aria_mode: "silent" | "reactive" | "proactive"
      session_status: "scheduled" | "in_progress" | "completed" | "aborted"
      transcript_speaker:
        | "surgeon"
        | "anaesthetist"
        | "nurse"
        | "aria"
        | "system"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      alert_severity: ["info", "caution", "warning", "critical"],
      app_role: ["admin", "surgeon", "anaesthetist"],
      aria_mode: ["silent", "reactive", "proactive"],
      session_status: ["scheduled", "in_progress", "completed", "aborted"],
      transcript_speaker: [
        "surgeon",
        "anaesthetist",
        "nurse",
        "aria",
        "system",
      ],
    },
  },
} as const
