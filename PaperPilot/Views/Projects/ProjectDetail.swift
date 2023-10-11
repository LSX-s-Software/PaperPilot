//
//  ProjectDetail.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/9/24.
//

import SwiftUI
import SwiftUIFlow

struct ProjectDetail: View {
    @Environment(\.openWindow) private var openWindow
    @Environment(\.modelContext) private var modelContext
    
    @Bindable var project: Project
    @State private var selection = Set<Paper.ID>()
    @State private var sortOrder = [KeyPathComparator(\Paper.formattedCreateTime)]
    @State private var isShowingEditProjectSheet = false
    @State private var isShowingAddPaperSheet = false
    
    var onDelete: (() -> Void)?
    
    var body: some View {
        Table(project.papers.sorted(using: sortOrder), selection: $selection, sortOrder: $sortOrder) {
            TableColumn("Title", value: \.title)
            TableColumn("Authors", value: \.formattedAuthors)
            TableColumn("Publication Year") { paper in
                Text(paper.publicationYear ?? "Unknown")
            }
            .width(50)
            TableColumn("Publication") { paper in
                Text(paper.publication ?? "Unknown")
            }
            TableColumn("Date Added", value: \.formattedCreateTime)
                .width(70)
            TableColumn("Tags") { paper in
                VFlow(alignment: .leading, spacing: 4) {
                    ForEach(paper.tags, id: \.self) { tag in
                        TagView(text: tag)
                    }
                }
                .clipped()
            }
            TableColumn("Read") { paper in
                if paper.read {
                    Image(systemName: "checkmark.circle.fill")
                }
            }
            .width(35)
        }
        .contextMenu(forSelectionType: Paper.ID.self) { selectedPapers in
            if !selectedPapers.isEmpty {
                Button("Mark as Read", systemImage: "checkmark.circle.fill") {
                    for paperId in selectedPapers {
                        if let index = project.papers.firstIndex(where: { $0.id == paperId }) {
                            project.papers[index].read = true
                        }
                    }
                }
                Button("Mark as Unread", systemImage: "circle") {
                    for paperId in selectedPapers {
                        if let index = project.papers.firstIndex(where: { $0.id == paperId }) {
                            project.papers[index].read = false
                        }
                    }
                }
                Button("Delete", systemImage: "trash", role: .destructive) {
                    for paperId in selectedPapers {
                        project.papers.removeAll { $0.id == paperId }
                    }
                }
            }
        } primaryAction: { selectedPapers in
            if selectedPapers.count == 1,
               let paperIndex = project.papers.firstIndex(where: { $0.id == selectedPapers.first! }) {
                openWindow(value: project.papers[paperIndex])
                project.papers[paperIndex].read = true
            }
        }
        .navigationTitle($project.name)
#if os(macOS)
        .navigationSubtitle(project.desc)
#endif
        .toolbar {
            ToolbarItemGroup {
                Button("Project Settings", systemImage: "folder.badge.gear") {
                    isShowingEditProjectSheet.toggle()
                }
                .sheet(isPresented: $isShowingEditProjectSheet) {
                    ProjectCreateEditView(edit: true, project: project, onDelete: onDelete)
                }
                
                Button("Add Document", systemImage: "plus") {
                    isShowingAddPaperSheet.toggle()
                }
                .sheet(isPresented: $isShowingAddPaperSheet) {
                    AddPaperView(project: project)
                }
            }
#if !os(macOS)
            ToolbarItem(placement: .navigationBarLeading) {
                EditButton()
            }
#endif
        }
    }
}

#Preview {
    ProjectDetail(project: ModelData.project1)
        .modelContainer(previewContainer)
#if os(macOS)
        .frame(width: 800, height: 600)
#endif
}
