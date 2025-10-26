import { createClient } from "@supabase/supabase-js";

const supabaseUrl = 'https://nynhpfozeopaaqkczcqs.supabase.coL';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im55bmhwZm96ZW9wYWFxa2N6Y3FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNTAxNTQsImV4cCI6MjA3NjkyNjE1NH0.Cn9Ke-dEiTVxQryfqI3MeuLruKUpV8bgjK-p3w7fKIE';

export const supabase = createClient(supabaseUrl, supabaseKey);