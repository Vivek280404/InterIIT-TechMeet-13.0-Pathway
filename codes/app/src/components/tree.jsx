import React, { useState, useMemo } from 'react';
import ReactFlow, { 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';

// Flexible graph node class
class GraphNode {
  constructor(value, metadata = {}) {
    this.value = value;
    this.children = []; // Can have multiple or no children
    this.metadata = metadata;
  }

  addChild(child) {
    this.children.push(child);
    return this;
  }
}

// Custom Node Component with Hover Effects
const CustomNode = ({ data }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className={`
        p-3 rounded-lg transition-all duration-200 ease-in-out
        ${isHovered 
          ? 'bg-blue-200 scale-105 shadow-xl' 
          : 'bg-blue-100 scale-100 shadow-md'
        }
        relative
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Handle type="target" position={Position.Left} />
      
      <div className="text-center">
        <p className="font-bold text-sm">{data.label}</p>
        
        {isHovered && data.metadata && (
          <div className="mt-2 text-xs text-gray-700">
            {Object.entries(data.metadata).map(([key, value]) => (
              <p key={key} className="mb-1">
                <span className="font-semibold">{key}:</span> {value}
              </p>
            ))}
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
};

// Node types definition
const nodeTypes = {
  custom: CustomNode
};

// Function to create a sample complex graph
const createSampleGraph = () => {
  // Create nodes with metadata
  const root = new GraphNode('Organization', {
    type: 'Root',
    founded: '2020',
    employees: '500+'
  });

  const engineering = new GraphNode('Engineering', {
    department: 'Technology',
    teams: '5',
    headcount: '150'
  });

  const product = new GraphNode('Product', {
    department: 'Innovation',
    teams: '3',
    headcount: '75'
  });

  const sales = new GraphNode('Sales', {
    department: 'Revenue',
    teams: '4',
    headcount: '100'
  });

  // Engineering sub-teams
  const frontend = new GraphNode('Frontend', {
    lead: 'Jane Doe',
    members: '30'
  });
  const backend = new GraphNode('Backend', {
    lead: 'John Smith',
    members: '40'
  });
  const devops = new GraphNode('DevOps', {
    lead: 'Alex Wong',
    members: '20'
  });

  // Product sub-teams
  const design = new GraphNode('Design', {
    lead: 'Emily Chen',
    members: '25'
  });
  const research = new GraphNode('Research', {
    lead: 'Michael Lee',
    members: '15'
  });

  // Build connections
  root.addChild(engineering)
      .addChild(product)
      .addChild(sales);

  engineering.addChild(frontend)
             .addChild(backend)
             .addChild(devops);

  product.addChild(design)
         .addChild(research);

  return root;
};

// Function to convert graph to React Flow elements
const convertGraphToFlowElements = (root) => {
  const nodes = [];
  const edges = [];
  
  // Recursive function to generate nodes and edges
  const traverseGraph = (node, x = 0, y = 0, level = 0, visited = new Set()) => {
    if (!node || visited.has(node)) return { x, y };

    visited.add(node);

    // Create node
    nodes.push({
      id: String(node.value),
      type: 'custom',
      position: { x, y },
      data: { 
        label: node.value,
        metadata: node.metadata
      }
    });

    // Calculate positions for children
    const childCount = node.children.length;
    const horizontalSpacing = childCount > 0 ? 200 / childCount : 0;

    // Add children
    node.children.forEach((child, index) => {
      // Calculate child position
      const childX = x - (horizontalSpacing * (childCount - 1) / 2) + (index * horizontalSpacing);
      const childY = y + 100;

      // Add edge
      edges.push({
        id: `edge-${node.value}-${child.value}`,
        source: String(node.value),
        target: String(child.value),
        style: { 
          stroke: '#3B82F6',
          strokeWidth: 2
        }
      });

      // Recursively process child
      traverseGraph(child, childX, childY, level + 1, visited);
    });

    return { nodes, edges };
  };

  return traverseGraph(root);
};

const FlexibleHoverGraph = () => {
  // Create sample graph
  const root = useMemo(() => createSampleGraph(), []);

  // Convert graph to React Flow elements
  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => 
    convertGraphToFlowElements(root), 
    [root]
  );

  // Use React Flow hooks
  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  return (
    <div style={{ height: '600px', width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="top-right"
      >
        <Controls />
        <Background color="#f0f0f0" gap={16} variant="dots" />
      </ReactFlow>
    </div>
  );
};

export default FlexibleHoverGraph;