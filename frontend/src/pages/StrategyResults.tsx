import { useLocation } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function StrategyResults() {
  const location = useLocation();
  const results = location.state?.results;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Strategy Results</h1>
      {results ? (
        <Card>
          <CardHeader><CardTitle>Results</CardTitle></CardHeader>
          <CardContent>
            <pre className="text-xs overflow-auto bg-muted p-4 rounded">{JSON.stringify(results, null, 2)}</pre>
          </CardContent>
        </Card>
      ) : <p className="text-muted-foreground">No strategy results to display.</p>}
    </div>
  );
}
